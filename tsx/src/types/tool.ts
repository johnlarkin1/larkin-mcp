export interface Metadata {
  mcp_version: string;
  mcp_website: string;
  resume_last_updated: string;
}

export interface ResourceStatus {
  available: boolean;
  size_bytes: number;
}

export interface HealthCheckResponse {
  status: string;
  version: string;
  resources: Record<string, ResourceStatus>;
}
