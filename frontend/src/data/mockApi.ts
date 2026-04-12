import { workspaceData } from "./mockData";
import type { WorkspaceData } from "../types";

export async function getWorkspaceData(): Promise<WorkspaceData> {
  await new Promise((resolve) => setTimeout(resolve, 120));
  return workspaceData;
}

export async function getProjectsData() {
  await new Promise((resolve) => setTimeout(resolve, 80));
  return workspaceData.projectRows;
}

