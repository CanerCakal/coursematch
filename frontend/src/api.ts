import type {
  Course,
  CourseComparisonHistoryResponse,
  CourseRecommendationItem,
  CourseRecommendationResponse,
  Department,
  ListResponse,
  University,
} from "./types";

const API_BASE_URL = "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = "İstek başarısız oldu.";

    try {
      const errorData = await response.json();
      message = errorData.detail ?? message;
    } catch {
      message = response.statusText || message;
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function getUniversities(): Promise<University[]> {
  return request<University[]>("/universities/");
}

export function getDepartments(params: {
  universityId?: number;
  search?: string;
  skip?: number;
  limit?: number;
}): Promise<ListResponse<Department>> {
  const searchParams = new URLSearchParams();

  if (params.universityId !== undefined) {
    searchParams.set("university_id", String(params.universityId));
  }

  if (params.search) {
    searchParams.set("search", params.search);
  }

  searchParams.set("skip", String(params.skip ?? 0));
  searchParams.set("limit", String(params.limit ?? 20));

  return request<ListResponse<Department>>(
    `/departments/?${searchParams.toString()}`
  );
}

export function getCourses(params: {
  departmentId?: number;
  search?: string;
  skip?: number;
  limit?: number;
}): Promise<ListResponse<Course>> {
  const searchParams = new URLSearchParams();

  if (params.departmentId !== undefined) {
    searchParams.set("department_id", String(params.departmentId));
  }

  if (params.search) {
    searchParams.set("search", params.search);
  }

  searchParams.set("skip", String(params.skip ?? 0));
  searchParams.set("limit", String(params.limit ?? 20));

  return request<ListResponse<Course>>(`/courses/?${searchParams.toString()}`);
}

export function getCourseRecommendations(params: {
  sourceCourseId: number;
  targetDepartmentId: number;
  limit?: number;
}): Promise<CourseRecommendationResponse> {
  return request<CourseRecommendationResponse>("/courses/recommendations", {
    method: "POST",
    body: JSON.stringify({
      source_course_id: params.sourceCourseId,
      target_department_id: params.targetDepartmentId,
      limit: params.limit ?? 5,
    }),
  });
}

export function compareCourses(params: {
  sourceCourseId: number;
  targetCourseId: number;
}): Promise<CourseRecommendationItem> {
  return request<CourseRecommendationItem>("/courses/compare", {
    method: "POST",
    body: JSON.stringify({
      source_course_id: params.sourceCourseId,
      target_course_id: params.targetCourseId,
    }),
  });
}

export function getComparisonHistory(params?: {
  skip?: number;
  limit?: number;
}): Promise<CourseComparisonHistoryResponse> {
  const searchParams = new URLSearchParams();

  searchParams.set("skip", String(params?.skip ?? 0));
  searchParams.set("limit", String(params?.limit ?? 5));

  return request<CourseComparisonHistoryResponse>(
    `/courses/comparisons?${searchParams.toString()}`
  );
}