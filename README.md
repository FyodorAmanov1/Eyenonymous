# Eyenonymous

**Detect faces from several viewing angles and inspect the effect of image preprocessing before applying a blur.**

Eyenonymous is a local computer-vision prototype built with OpenCV and NumPy. It combines frontal and profile Haar cascades, handles mirrored profile views and removes overlapping detections before blurring detected regions.

## Features

- Frontal and profile detection using multiple OpenCV cascade classifiers.
- Horizontal flipping for the opposite profile direction.
- Non-maximum suppression to reduce duplicate boxes.
- Optional preprocessing, including contrast enhancement, for side-by-side inspection.
- Webcam preview with adjustable blur and snapshot capture.
- A snapshot mode when an interactive OpenCV window is unavailable.

## Run the camera demo

Use a Python environment with a connected camera and desktop GUI support:

```bash
python -m pip install opencv-python numpy
python opencv.py
```

The script opens camera index 0. OpenCV supplies the cascade files through its installed data directory.

| Key | Action |
|---|---|
| `q` | Quit and release the camera |
| `b` | Toggle face blurring |
| `s` | Save the displayed frame |
| `+` / `-` | Increase / decrease blur intensity |

The non-GUI fallback saves original, preprocessed and blurred image sets. Be aware of which files are being written when capturing people.

## Explore the detector

The main `FaceDetectorBlur` class is in [opencv.py](opencv.py). Its methods expose detection, preprocessing and region blurring independently of the camera demonstration. See the [multi-angle implementation guide](MULTI_ANGLE_DETECTION.md) for classifier selection and output formats.

## Interpreting detection output

The displayed confidence values are heuristic scores, not calibrated probabilities or a measured recognition accuracy. The repository does not include a labeled evaluation dataset supporting the percentage improvements quoted in the older implementation guide.

Haar cascades can miss small, occluded or unusually posed faces. Detection followed by blur is therefore an assistive editing technique, not a guarantee that every person in an image has been anonymized. Inspect exported frames before sharing them.
