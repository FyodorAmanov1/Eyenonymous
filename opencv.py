import cv2
import numpy as np


class FaceDetectorBlur:
    """
    A class to detect faces in images and apply blur to detected face regions.
    Uses OpenCV's Haar Cascade classifier for face detection.
    
    Features:
    - Face detection with confidence scores
    - Multiple preprocessing methods to enhance face contrast from background:
        * CLAHE (Contrast Limited Adaptive Histogram Equalization) - Best for faces
        * Histogram Equalization - Global contrast enhancement
        * Sharpening - Edge enhancement
        * Combined - All methods together
    - Face blurring for privacy
    - Real-time camera capture support
    """
    
    def __init__(self, cascade_path=None, use_multi_angle=True):
        """
        Initialize the face detector with multi-angle support.
        
        Args:
            cascade_path: Path to Haar Cascade XML file. If None, uses default.
            use_multi_angle: If True, uses multiple cascades for different angles.
        """
        self.use_multi_angle = use_multi_angle
        
        # Load multiple cascades for different face orientations
        haarcascades_path = cv2.data.haarcascades
        
        # Primary frontal face detector
        if cascade_path is None:
            cascade_path = haarcascades_path + 'haarcascade_frontalface_default.xml'
        
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            raise ValueError(f"Failed to load cascade classifier from {cascade_path}")
        
        # Additional cascades for multi-angle detection
        self.cascades = {
            'frontal_default': self.face_cascade,
        }
        
        if use_multi_angle:
            # Alternative frontal face detector (more sensitive)
            alt_cascade = cv2.CascadeClassifier(haarcascades_path + 'haarcascade_frontalface_alt.xml')
            if not alt_cascade.empty():
                self.cascades['frontal_alt'] = alt_cascade
            
            # Alternative frontal face detector 2 (even more sensitive)
            alt2_cascade = cv2.CascadeClassifier(haarcascades_path + 'haarcascade_frontalface_alt2.xml')
            if not alt2_cascade.empty():
                self.cascades['frontal_alt2'] = alt2_cascade
            
            # Profile face detector (side views)
            profile_cascade = cv2.CascadeClassifier(haarcascades_path + 'haarcascade_profileface.xml')
            if not profile_cascade.empty():
                self.cascades['profile'] = profile_cascade
        
        print(f"✓ Loaded {len(self.cascades)} cascade classifier(s) for face detection")
        for name in self.cascades.keys():
            print(f"  - {name}")
    
    def detect_faces(self, image, return_confidence=False, min_confidence=60):
        """
        Detect faces in the given image using multiple cascades for different angles.
        
        Args:
            image: Input image (BGR format)
            return_confidence: If True, returns confidence scores with detections
            min_confidence: Minimum confidence threshold (0-100) to accept detection
            
        Returns:
            If return_confidence=False: List of tuples (x, y, w, h)
            If return_confidence=True: List of tuples (x, y, w, h, confidence, angle_type)
        """
        # Convert to grayscale for detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        all_faces = []
        face_sources = {}  # Track which cascade detected which face
        
        # Detect with each cascade
        for cascade_name, cascade in self.cascades.items():
            # Adjust parameters based on cascade type
            if 'profile' in cascade_name:
                # Profile faces are harder to detect, use more lenient parameters
                scale_factor = 1.05
                min_neighbors = 3
            else:
                # Frontal faces - use stricter parameters to reduce false positives
                scale_factor = 1.15  # Increased from 1.1 to reduce false positives
                min_neighbors = 7    # Increased from 5 to reduce false positives
            
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=(40, 40),  # Increased from 30x30 to avoid tiny false positives
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            for face in faces:
                all_faces.append(face)
                face_sources[tuple(face)] = cascade_name
        
        # If profile detection is enabled, also check mirrored image for left-facing profiles
        if self.use_multi_angle and 'profile' in self.cascades:
            flipped_gray = cv2.flip(gray, 1)
            profile_faces = self.cascades['profile'].detectMultiScale(
                flipped_gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(40, 40)
            )
            
            # Convert coordinates back to original orientation
            width = image.shape[1]
            for (x, y, w, h) in profile_faces:
                # Flip x coordinate back
                original_x = width - x - w
                mirrored_face = (original_x, y, w, h)
                all_faces.append(mirrored_face)
                face_sources[mirrored_face] = 'profile_left'
        
        if len(all_faces) == 0:
            return [] if not return_confidence else []
        
        # Remove duplicate detections using Non-Maximum Suppression (NMS)
        unique_faces = self._apply_nms(all_faces, face_sources, overlap_threshold=0.3)
        
        # Validate faces and calculate confidence
        validated_faces = []
        for (x, y, w, h, source) in unique_faces:
            # Validate the face region
            is_valid, confidence_adjustment = self._validate_face_region(image, (x, y, w, h))
            
            if not is_valid:
                continue  # Skip this detection
            
            # Calculate base confidence
            confidence = self._calculate_confidence(gray, (x, y, w, h), source)
            
            # Apply validation adjustment
            confidence += confidence_adjustment
            confidence = max(0, min(100, confidence))  # Clamp to 0-100
            
            # Filter by minimum confidence
            if confidence < min_confidence:
                continue
            
            # Determine angle type from source
            if 'profile' in source:
                angle_type = 'profile' if source == 'profile' else 'profile_left'
            else:
                angle_type = 'frontal'
            
            validated_faces.append((x, y, w, h, confidence, angle_type))
        
        if not return_confidence:
            return np.array([(x, y, w, h) for x, y, w, h, _, _ in validated_faces])
        
        return validated_faces
    
    def _apply_nms(self, faces, face_sources, overlap_threshold=0.3):
        """
        Apply Non-Maximum Suppression to remove duplicate detections.
        
        Args:
            faces: List of face bounding boxes
            face_sources: Dictionary mapping faces to their detection source
            overlap_threshold: IoU threshold for considering faces as duplicates
            
        Returns:
            List of unique faces with their sources
        """
        if len(faces) == 0:
            return []
        
        # Convert to numpy array for easier manipulation
        boxes = np.array(faces)
        
        # Calculate areas
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 0] + boxes[:, 2]
        y2 = boxes[:, 1] + boxes[:, 3]
        areas = boxes[:, 2] * boxes[:, 3]
        
        # Sort by area (larger faces first - generally more reliable)
        order = areas.argsort()[::-1]
        
        keep = []
        while len(order) > 0:
            i = order[0]
            keep.append(i)
            
            # Calculate IoU with remaining boxes
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            
            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)
            
            intersection = w * h
            union = areas[i] + areas[order[1:]] - intersection
            iou = intersection / union
            
            # Keep only boxes with IoU below threshold
            order = order[np.where(iou <= overlap_threshold)[0] + 1]
        
        # Return unique faces with their sources
        unique_faces = []
        for idx in keep:
            face_tuple = tuple(faces[idx])
            source = face_sources.get(face_tuple, 'unknown')
            unique_faces.append((*faces[idx], source))
        
        return unique_faces
    
    def _calculate_confidence(self, gray, face_box, source):
        """
        Calculate confidence score for a detected face.
        
        Args:
            gray: Grayscale image
            face_box: (x, y, w, h) tuple
            source: Detection source (cascade name)
            
        Returns:
            Confidence score (0-100)
        """
        x, y, w, h = face_box
        
        # Base confidence from source
        base_confidence = {
            'frontal_default': 85,
            'frontal_alt': 75,
            'frontal_alt2': 70,
            'profile': 65,
            'profile_left': 65,
            'unknown': 60
        }.get(source, 60)
        
        # Size factor (larger faces = more reliable)
        size_factor = min(1.0, (w * h) / (100 * 100))
        
        # Extract face region and check quality
        face_region = gray[y:y+h, x:x+w]
        if face_region.size == 0:
            return base_confidence
        
        # Check contrast/variance (higher = more distinct features)
        variance = np.var(face_region)
        contrast_factor = min(1.0, variance / 1000.0)
        
        # Combined confidence
        confidence = base_confidence * (0.6 + 0.2 * size_factor + 0.2 * contrast_factor)
        confidence = min(100, max(0, confidence))
        
        return confidence
    
    def _calculate_iou(self, box1, box2):
        """
        Calculate Intersection over Union (IoU) between two bounding boxes.
        
        Args:
            box1, box2: Tuples of (x, y, w, h)
            
        Returns:
            IoU score between 0 and 1
        """
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def _validate_face_region(self, image, face_box):
        """
        Validate if detected region is likely a real face (not false positive).
        Uses multiple heuristics to filter out non-face regions.
        
        Args:
            image: Input image (BGR format)
            face_box: (x, y, w, h) tuple
            
        Returns:
            Tuple (is_valid, confidence_adjustment)
        """
        x, y, w, h = face_box
        
        # Extract face region
        if y + h > image.shape[0] or x + w > image.shape[1]:
            return False, 0
        
        face_region = image[y:y+h, x:x+w]
        
        if face_region.size == 0:
            return False, 0
        
        # Convert to grayscale for analysis
        if len(face_region.shape) == 3:
            gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            gray_face = face_region
        
        # Heuristic 1: Check aspect ratio (faces are roughly square, 0.7-1.3 ratio)
        aspect_ratio = w / h if h > 0 else 0
        if aspect_ratio < 0.6 or aspect_ratio > 1.5:
            return False, -20  # Too elongated or too wide
        
        # Heuristic 2: Check if region is in lower part of image (torsos often detected there)
        img_height = image.shape[0]
        vertical_position = (y + h/2) / img_height
        
        # If detection is in bottom 40% of image, be more skeptical
        if vertical_position > 0.6:
            confidence_penalty = -15
        else:
            confidence_penalty = 0
        
        # Heuristic 3: Check texture complexity (faces have more varied texture)
        # Calculate edge density using Sobel operator
        sobelx = cv2.Sobel(gray_face, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray_face, cv2.CV_64F, 0, 1, ksize=3)
        edge_magnitude = np.sqrt(sobelx**2 + sobely**2)
        edge_density = np.mean(edge_magnitude)
        
        # Faces typically have edge density between 10-50
        if edge_density < 5:
            return False, -30  # Too uniform (might be clothing/wall)
        elif edge_density > 80:
            return False, -25  # Too noisy (might be texture pattern)
        
        # Heuristic 4: Check brightness distribution
        # Faces have characteristic brightness patterns (eyes darker, forehead/cheeks lighter)
        top_third = gray_face[0:h//3, :]
        middle_third = gray_face[h//3:2*h//3, :]
        bottom_third = gray_face[2*h//3:h, :]
        
        top_brightness = np.mean(top_third) if top_third.size > 0 else 0
        middle_brightness = np.mean(middle_third) if middle_third.size > 0 else 0
        bottom_brightness = np.mean(bottom_third) if bottom_third.size > 0 else 0
        
        # Check if middle is darker than top/bottom (eyes/nose region)
        brightness_variation = np.std([top_brightness, middle_brightness, bottom_brightness])
        
        if brightness_variation < 5:
            confidence_penalty -= 10  # Too uniform brightness
        
        # Heuristic 5: Skin color detection (if in lower image, check for skin tones)
        if vertical_position > 0.6:
            # Convert to HSV for better skin detection
            hsv_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2HSV)
            
            # Skin color range in HSV
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            skin_mask = cv2.inRange(hsv_face, lower_skin, upper_skin)
            skin_ratio = np.sum(skin_mask > 0) / skin_mask.size
            
            # If very high skin ratio in lower image, likely torso/arms not face
            if skin_ratio > 0.7 and edge_density < 15:
                return False, -35  # Uniform skin-colored region = probably body
        
        # Heuristic 6: Size check - very large detections in lower frame are suspicious
        detection_area = w * h
        image_area = image.shape[0] * image.shape[1]
        area_ratio = detection_area / image_area
        
        if area_ratio > 0.15 and vertical_position > 0.5:
            confidence_penalty -= 20  # Large detection in lower frame
        
        # Calculate final validation
        total_penalty = confidence_penalty
        
        # If penalties are too severe, reject
        if total_penalty < -40:
            return False, total_penalty
        
        return True, total_penalty
    
    def preprocess_image(self, image, method='auto'):
        """
        Preprocess image to enhance face contrast from background.
        
        Args:
            image: Input image (BGR format)
            method: Preprocessing method - 'auto', 'histogram', 'clahe', 'sharpen', 'all'
            
        Returns:
            Preprocessed image
        """
        if method == 'histogram':
            return self._histogram_equalization(image)
        elif method == 'clahe':
            return self._apply_clahe(image)
        elif method == 'sharpen':
            return self._sharpen_image(image)
        elif method == 'all':
            # Apply multiple preprocessing steps
            result = self._histogram_equalization(image)
            result = self._apply_clahe(result)
            result = self._sharpen_image(result)
            return result
        else:  # 'auto'
            # Apply CLAHE which works best for face detection
            return self._apply_clahe(image)
    
    def _histogram_equalization(self, image):
        """Apply histogram equalization to enhance contrast."""
        # Convert to YCrCb color space
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        
        # Equalize the Y channel (luminance)
        ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
        
        # Convert back to BGR
        result = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
        return result
    
    def _apply_clahe(self, image):
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).
        This is very effective for face detection as it enhances local contrast.
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Split channels
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels
        lab = cv2.merge([l, a, b])
        
        # Convert back to BGR
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        return result
    
    def _sharpen_image(self, image):
        """Apply sharpening filter to enhance edges and details."""
        # Create sharpening kernel
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        
        # Apply the kernel
        sharpened = cv2.filter2D(image, -1, kernel)
        
        # Blend with original to avoid over-sharpening
        result = cv2.addWeighted(image, 0.5, sharpened, 0.5, 0)
        return result
    
    def detect_faces_with_preprocessing(self, image, preprocess_method='auto', return_confidence=False, min_confidence=60):
        """
        Detect faces with automatic preprocessing to enhance detection.
        
        Args:
            image: Input image (BGR format)
            preprocess_method: Method for preprocessing ('auto', 'histogram', 'clahe', 'sharpen', 'all')
            return_confidence: If True, returns confidence scores
            min_confidence: Minimum confidence threshold (0-100) to accept detection
            
        Returns:
            Tuple of (faces, preprocessed_image)
        """
        # Preprocess the image
        preprocessed = self.preprocess_image(image, method=preprocess_method)
        
        # Detect faces on preprocessed image with validation
        faces = self.detect_faces(preprocessed, return_confidence=return_confidence, min_confidence=min_confidence)
        
        return faces, preprocessed
    
    def blur_faces(self, image, faces, blur_intensity=51):
        """
        Apply Gaussian blur to detected face regions.
        
        Args:
            image: Input image (BGR format)
            faces: List of face bounding boxes (x, y, w, h)
            blur_intensity: Blur kernel size (must be odd). Higher = more blur.
            
        Returns:
            Image with blurred faces
        """
        # Make a copy to avoid modifying the original
        result = image.copy()
        
        # Ensure blur_intensity is odd
        if blur_intensity % 2 == 0:
            blur_intensity += 1
        
        # Blur each detected face
        for (x, y, w, h) in faces:
            # Extract face region
            face_region = result[y:y+h, x:x+w]
            
            # Apply Gaussian blur
            blurred_face = cv2.GaussianBlur(face_region, (blur_intensity, blur_intensity), 0)
            
            # Replace the face region with blurred version
            result[y:y+h, x:x+w] = blurred_face
        
        return result
    
    def draw_face_boxes(self, image, faces, color=(0, 255, 0), thickness=2):
        """
        Draw bounding boxes around detected faces.
        
        Args:
            image: Input image (BGR format)
            faces: List of face bounding boxes (x, y, w, h)
            color: Box color in BGR format
            thickness: Box line thickness
            
        Returns:
            Image with drawn bounding boxes
        """
        result = image.copy()
        
        for (x, y, w, h) in faces:
            cv2.rectangle(result, (x, y), (x+w, y+h), color, thickness)
        
        return result
    
    def process_image(self, image_path, output_path=None, show_boxes=False, blur_intensity=51, show_confidence=True):
        """
        Complete pipeline: load image, detect faces, blur them, and optionally save.
        
        Args:
            image_path: Path to input image
            output_path: Path to save output image (None = don't save)
            show_boxes: If True, draw boxes around faces before blurring
            blur_intensity: Blur kernel size
            show_confidence: If True, display confidence scores
            
        Returns:
            Tuple of (processed_image, faces_detected_with_confidence)
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image from {image_path}")
        
        # Detect faces with confidence
        faces_with_conf = self.detect_faces(image, return_confidence=True)
        print(f"Detected {len(faces_with_conf)} face(s)")
        
        # Print face locations and confidence
        for i, (x, y, w, h, confidence) in enumerate(faces_with_conf):
            print(f"Face {i+1}: Location=(x:{x}, y:{y}), Size=(w:{w}, h:{h})")
            if show_confidence:
                print(f"          Confidence: {confidence:.2f}%")
        
        # Extract faces without confidence for blurring
        faces = [(x, y, w, h) for x, y, w, h, _ in faces_with_conf]
        
        # Optionally draw boxes
        if show_boxes:
            for (x, y, w, h, confidence) in faces_with_conf:
                # Color based on confidence
                if confidence > 70:
                    color = (0, 255, 0)  # Green
                elif confidence > 50:
                    color = (0, 255, 255)  # Yellow
                else:
                    color = (0, 0, 255)  # Red
                
                cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)
                if show_confidence:
                    conf_text = f"{confidence:.1f}%"
                    cv2.putText(image, conf_text, (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Blur faces
        result = self.blur_faces(image, faces, blur_intensity)
        
        # Save if output path provided
        if output_path:
            cv2.imwrite(output_path, result)
            print(f"Saved result to {output_path}")
        
        return result, faces_with_conf


def main():
    """
    Capture images from camera and apply face detection and blurring.
    Two modes available: GUI mode (if OpenCV GUI is available) or snapshot mode.
    """
    print("=" * 60)
    print("Face Detection and Blur - Camera Mode")
    print("=" * 60)
    
    # Initialize the face detector
    try:
        detector = FaceDetectorBlur()
        print("✓ Face detector initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize face detector: {e}")
        return
    
    # Open the camera (0 is usually the default camera)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("✗ Error: Could not open camera")
        print("  Make sure your camera is connected and not being used by another application")
        return
    
    print("✓ Camera opened successfully")
    
    # Check if GUI is available
    try:
        # Try to create a test window
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imshow('test', test_frame)
        cv2.destroyWindow('test')
        cv2.waitKey(1)
        gui_available = True
    except:
        gui_available = False
    
    if gui_available:
        print("\n✓ OpenCV GUI available - Starting interactive mode")
        print("Controls:")
        print("  - Press 'q' to quit")
        print("  - Press 's' to save a snapshot")
        print("  - Press 'b' to toggle blur on/off")
        print("  - Press '+' to increase blur intensity")
        print("  - Press '-' to decrease blur intensity")
        print("=" * 60)
        run_gui_mode(cap, detector)
    else:
        print("\n⚠ OpenCV GUI not available - Starting snapshot mode")
        print("This will capture images from your camera and save them.")
        print("=" * 60)
        run_snapshot_mode(cap, detector)


def run_gui_mode(cap, detector):
    """Run interactive GUI mode with live video feed."""
    blur_enabled = True
    blur_intensity = 51
    snapshot_counter = 0
    
    print("\nStarting video capture...")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("✗ Failed to grab frame")
            break
        
        faces = detector.detect_faces(frame)
        
        if blur_enabled and len(faces) > 0:
            display_frame = detector.blur_faces(frame, faces, blur_intensity)
        else:
            display_frame = frame.copy()
        
        for (x, y, w, h) in faces:
            color = (0, 255, 0) if blur_enabled else (255, 0, 0)
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(display_frame, 'Face', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        info_text = f"Faces: {len(faces)} | Blur: {'ON' if blur_enabled else 'OFF'} | Intensity: {blur_intensity}"
        cv2.putText(display_frame, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        cv2.imshow('Face Detection & Blur (Press Q to quit)', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\nQuitting...")
            break
        elif key == ord('s'):
            snapshot_counter += 1
            filename = f'snapshot_{snapshot_counter}.jpg'
            cv2.imwrite(filename, display_frame)
            print(f"✓ Saved snapshot: {filename}")
        elif key == ord('b'):
            blur_enabled = not blur_enabled
            status = "enabled" if blur_enabled else "disabled"
            print(f"Blur {status}")
        elif key == ord('+') or key == ord('='):
            blur_intensity = min(blur_intensity + 10, 199)
            if blur_intensity % 2 == 0:
                blur_intensity += 1
            print(f"Blur intensity: {blur_intensity}")
        elif key == ord('-') or key == ord('_'):
            blur_intensity = max(blur_intensity - 10, 11)
            if blur_intensity % 2 == 0:
                blur_intensity += 1
            print(f"Blur intensity: {blur_intensity}")
    
    cap.release()
    cv2.destroyAllWindows()
    print("✓ Camera released and windows closed")
    print(f"✓ Total snapshots saved: {snapshot_counter}")


def run_snapshot_mode(cap, detector):
    """Run snapshot mode - capture and save images without GUI."""
    import time
    
    blur_intensity = 51
    num_snapshots = 60
    delay = 1/60  # seconds between captures
    preprocess_method = 'clahe'  # Use CLAHE for best face contrast
    
    print(f"\nWill capture {num_snapshots} images with {delay} second delay between each.")
    print(f"Using preprocessing method: {preprocess_method.upper()} (enhances face contrast)")
    print("Position yourself in front of the camera...")
    print()
    
    # Track statistics
    all_confidences = []
    preprocessed_confidences = []
    
    for i in range(num_snapshots):
        print(f"Capturing image {i+1}/{num_snapshots}...", end=" ")
        
        ret, frame = cap.read()
        
        if not ret:
            print("✗ Failed to grab frame")
            break
        
        # Detect faces WITHOUT preprocessing (baseline)
        faces_baseline = detector.detect_faces(frame, return_confidence=True)
        
        # Detect faces WITH preprocessing (enhanced)
        faces_with_conf, preprocessed_frame = detector.detect_faces_with_preprocessing(
            frame, 
            preprocess_method=preprocess_method,
            return_confidence=True
        )
        
        print(f"[Baseline: {len(faces_baseline)}, Enhanced: {len(faces_with_conf)} face(s) detected]")
        
        # Save original
        original_filename = f'camera_original_{i+1}.jpg'
        cv2.imwrite(original_filename, frame)
        print(f"  ✓ Saved original: {original_filename}")
        
        # Save preprocessed (enhanced contrast)
        preprocessed_filename = f'camera_preprocessed_{i+1}.jpg'
        cv2.imwrite(preprocessed_filename, preprocessed_frame)
        print(f"  ✓ Saved preprocessed: {preprocessed_filename}")
        
        if len(faces_with_conf) > 0:
            # Print face locations, confidence, and angle
            for j, face_data in enumerate(faces_with_conf):
                if len(face_data) == 6:  # With angle info
                    x, y, w, h, confidence, angle_type = face_data
                    angle_emoji = '👤' if angle_type == 'frontal' else '👥'
                    print(f"    Face {j+1}: Location=(x:{x}, y:{y}), Size=(w:{w}, h:{h})")
                    print(f"            Confidence: {confidence:.2f}% {'🟢' if confidence > 70 else '🟡' if confidence > 50 else '🔴'}")
                    print(f"            Angle: {angle_type} {angle_emoji}")
                else:  # Without angle info
                    x, y, w, h, confidence = face_data
                    print(f"    Face {j+1}: Location=(x:{x}, y:{y}), Size=(w:{w}, h:{h})")
                    print(f"            Confidence: {confidence:.2f}% {'🟢' if confidence > 70 else '🟡' if confidence > 50 else '🔴'}")
                preprocessed_confidences.append(confidence)
            
            # Also collect baseline confidences for comparison
            for j, face_data in enumerate(faces_baseline):
                if len(face_data) >= 5:
                    confidence = face_data[4]
                    all_confidences.append(confidence)
            
            # Create blurred version on ORIGINAL frame (extract x,y,w,h only)
            faces = []
            for face_data in faces_with_conf:
                if len(face_data) == 6:  # With angle
                    x, y, w, h, confidence, angle_type = face_data
                else:  # Without angle
                    x, y, w, h, confidence = face_data
                faces.append((x, y, w, h))
            
            blurred_frame = detector.blur_faces(frame, faces, blur_intensity)
            
            # Draw boxes on blurred version with confidence and angle labels
            for face_data in faces_with_conf:
                if len(face_data) == 6:  # With angle
                    x, y, w, h, confidence, angle_type = face_data
                    label_text = f"{confidence:.1f}% ({angle_type})"
                else:  # Without angle
                    x, y, w, h, confidence = face_data
                    label_text = f"{confidence:.1f}%"
                
                # Color based on confidence: green (high), yellow (medium), red (low)
                if confidence > 70:
                    color = (0, 255, 0)  # Green
                elif confidence > 50:
                    color = (0, 255, 255)  # Yellow
                else:
                    color = (0, 0, 255)  # Red
                
                cv2.rectangle(blurred_frame, (x, y), (x+w, y+h), color, 2)
                
                # Add confidence and angle text on image
                cv2.putText(blurred_frame, label_text, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            blurred_filename = f'camera_blurred_{i+1}.jpg'
            cv2.imwrite(blurred_filename, blurred_frame)
            print(f"  ✓ Saved blurred: {blurred_filename}")
        else:
            print("    ℹ No faces detected in enhanced image, skipping blur")
        
        print()
        
        if i < num_snapshots - 1:
            time.sleep(delay)
    
    cap.release()
    print("=" * 60)
    print(f"✓ Capture complete! Saved {num_snapshots} image sets")
    print("✓ Camera released")
    
    # Print statistics
    print("\n" + "=" * 60)
    print("DETECTION STATISTICS:")
    print("=" * 60)
    
    if preprocessed_confidences:
        avg_conf_enhanced = sum(preprocessed_confidences) / len(preprocessed_confidences)
        min_conf_enhanced = min(preprocessed_confidences)
        max_conf_enhanced = max(preprocessed_confidences)
        
        print(f"\nWith Preprocessing ({preprocess_method.upper()}):")
        print(f"  Total faces detected: {len(preprocessed_confidences)}")
        print(f"  Average confidence: {avg_conf_enhanced:.2f}%")
        print(f"  Minimum confidence: {min_conf_enhanced:.2f}%")
        print(f"  Maximum confidence: {max_conf_enhanced:.2f}%")
    
    if all_confidences:
        avg_conf_baseline = sum(all_confidences) / len(all_confidences)
        min_conf_baseline = min(all_confidences)
        max_conf_baseline = max(all_confidences)
        
        print(f"\nWithout Preprocessing (Baseline):")
        print(f"  Total faces detected: {len(all_confidences)}")
        print(f"  Average confidence: {avg_conf_baseline:.2f}%")
        print(f"  Minimum confidence: {min_conf_baseline:.2f}%")
        print(f"  Maximum confidence: {max_conf_baseline:.2f}%")
        
        if preprocessed_confidences:
            improvement = avg_conf_enhanced - avg_conf_baseline
            improvement_pct = (improvement / avg_conf_baseline) * 100 if avg_conf_baseline > 0 else 0
            print(f"\n✨ Improvement with preprocessing:")
            print(f"  Confidence boost: {improvement:+.2f}% ({improvement_pct:+.1f}%)")
            print(f"  More faces detected: {len(preprocessed_confidences) - len(all_confidences)}")
    
    print("=" * 60)
    
    print("\nTo use GUI mode, install opencv-python with GUI support:")
    print("  pip uninstall opencv-python-headless")
    print("  pip install opencv-python")


if __name__ == "__main__":
    main()
