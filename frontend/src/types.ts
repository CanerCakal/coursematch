export type University = {
  id: number;
  name: string;
  city: string | null;
  country: string | null;
  website: string | null;
};

export type Department = {
  id: number;
  university_id: number;
  name: string;
  faculty: string | null;
};

export type Course = {
  id: number;
  department_id: number;
  code: string | null;
  name: string;
  language: string | null;
  ects: number | null;
  credit: number | null;
  description: string | null;
  weekly_plan: string | null;
  learning_outcomes: string | null;
  resources: string | null;
};

export type ListResponse<T> = {
  total: number;
  skip: number;
  limit: number;
  items: T[];
};

export type CourseRecommendationItem = {
  source_course_id: number;
  source_course_name: string;
  target_course_id: number;
  target_course_name: string;
  similarity_score: number;
  keyword_similarity_score: number;
  ects_match: boolean;
  credit_match: boolean;
  matched_keywords: string[];
  recommendation: string;
  summary: string;
};

export type CourseRecommendationResponse = {
  source_course_id: number;
  source_course_name: string;
  target_department_id: number;
  total_candidates: number;
  limit: number;
  items: CourseRecommendationItem[];
};

export type CourseComparisonHistoryItem = CourseRecommendationItem & {
  id: number;
  created_at: string;
};

export type CourseComparisonHistoryResponse = {
  total: number;
  skip: number;
  limit: number;
  items: CourseComparisonHistoryItem[];
};