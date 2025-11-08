/**
 * Mock detection data generator for demo purposes
 * Use when Jetson hardware is not available
 */

type MockDetection = {
  id: number;
  deviceId: string;
  scene: string | null;
  labels: Array<{ name: string; conf: number }>;
  createdAt: string;
};

const MOCK_DEVICES = ['jetson-001', 'jetson-002', 'jetson-003'];
const MOCK_SCENES = ['office', 'lobby', 'parking', 'entrance', 'hallway', null];
const MOCK_LABELS = [
  { name: 'person', weight: 0.4 },
  { name: 'laptop', weight: 0.2 },
  { name: 'phone', weight: 0.15 },
  { name: 'backpack', weight: 0.1 },
  { name: 'chair', weight: 0.08 },
  { name: 'monitor', weight: 0.07 },
];

function randomChoice<T>(items: T[]): T {
  return items[Math.floor(Math.random() * items.length)];
}

function randomFloat(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

function generateMockLabels(): Array<{ name: string; conf: number }> {
  const count = Math.floor(Math.random() * 3) + 1; // 1-3 labels
  const selected = new Set<string>();
  const labels: Array<{ name: string; conf: number }> = [];

  while (labels.length < count && selected.size < MOCK_LABELS.length) {
    const label = randomChoice(MOCK_LABELS);
    if (!selected.has(label.name)) {
      selected.add(label.name);
      labels.push({
        name: label.name,
        conf: randomFloat(0.75, 0.98),
      });
    }
  }

  return labels;
}

let mockIdCounter = 1;

export function generateMockDetection(): MockDetection {
  const now = new Date();
  const createdAt = new Date(now.getTime() - Math.random() * 60000).toISOString(); // Within last minute

  return {
    id: mockIdCounter++,
    deviceId: randomChoice(MOCK_DEVICES),
    scene: Math.random() > 0.3 ? randomChoice(MOCK_SCENES) : null,
    labels: generateMockLabels(),
    createdAt,
  };
}

export function generateMockDetections(count: number = 20): MockDetection[] {
  return Array.from({ length: count }, () => generateMockDetection());
}

/**
 * Simulate real-time detection updates
 * Returns a function that generates new detections periodically
 */
export function createMockDetectionStream(
  onDetection: (detection: MockDetection) => void,
  intervalMs: number = 2000
): () => void {
  const intervalId = setInterval(() => {
    const detection = generateMockDetection();
    onDetection(detection);
  }, intervalMs);

  return () => clearInterval(intervalId);
}

