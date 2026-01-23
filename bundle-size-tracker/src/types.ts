export interface BundleSize {
  raw: number;
  gzipped: number;
}

export interface SizeEntry {
  commit: string;
  timestamp: number;
  sizes: Record<string, BundleSize>;
  total: BundleSize;
}

export interface Config {
  buildCommand?: string;
  outputDirs: string[];
  filePatterns: string[];
  thresholds: {
    total: number;
    perFile: number;
  };
}