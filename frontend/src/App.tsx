import { useEffect, useMemo, useState } from "react";

import {
  getCourseRecommendations,
  getCourses,
  getDepartments,
  getUniversities,
} from "./api";
import type {
  Course,
  CourseRecommendationItem,
  Department,
  University,
} from "./types";

import "./App.css";

function App() {
  const [universities, setUniversities] = useState<University[]>([]);

  const [sourceUniversityId, setSourceUniversityId] = useState<number | "">("");
  const [sourceDepartmentId, setSourceDepartmentId] = useState<number | "">("");
  const [sourceCourseId, setSourceCourseId] = useState<number | "">("");

  const [targetUniversityId, setTargetUniversityId] = useState<number | "">("");
  const [targetDepartmentId, setTargetDepartmentId] = useState<number | "">("");

  const [sourceDepartments, setSourceDepartments] = useState<Department[]>([]);
  const [targetDepartments, setTargetDepartments] = useState<Department[]>([]);
  const [sourceCourses, setSourceCourses] = useState<Course[]>([]);

  const [recommendations, setRecommendations] = useState<
    CourseRecommendationItem[]
  >([]);

  const [totalCandidates, setTotalCandidates] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecommendationLoading, setIsRecommendationLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const selectedSourceCourse = useMemo(() => {
    if (sourceCourseId === "") {
      return null;
    }

    return sourceCourses.find((course) => course.id === sourceCourseId) ?? null;
  }, [sourceCourseId, sourceCourses]);

  useEffect(() => {
    async function loadUniversities() {
      try {
        setIsLoading(true);
        setErrorMessage(null);

        const data = await getUniversities();
        setUniversities(data);
      } catch (error) {
        setErrorMessage(
          error instanceof Error
            ? error.message
            : "Üniversiteler yüklenirken hata oluştu."
        );
      } finally {
        setIsLoading(false);
      }
    }

    loadUniversities();
  }, []);

  useEffect(() => {
    async function loadSourceDepartments() {
      if (sourceUniversityId === "") {
        setSourceDepartments([]);
        setSourceDepartmentId("");
        setSourceCourses([]);
        setSourceCourseId("");
        return;
      }

      try {
        setErrorMessage(null);

        const data = await getDepartments({
          universityId: sourceUniversityId,
          limit: 100,
        });

        setSourceDepartments(data.items);
        setSourceDepartmentId("");
        setSourceCourses([]);
        setSourceCourseId("");
      } catch (error) {
        setErrorMessage(
          error instanceof Error
            ? error.message
            : "Kaynak bölümler yüklenirken hata oluştu."
        );
      }
    }

    loadSourceDepartments();
  }, [sourceUniversityId]);

  useEffect(() => {
    async function loadTargetDepartments() {
      if (targetUniversityId === "") {
        setTargetDepartments([]);
        setTargetDepartmentId("");
        return;
      }

      try {
        setErrorMessage(null);

        const data = await getDepartments({
          universityId: targetUniversityId,
          limit: 100,
        });

        setTargetDepartments(data.items);
        setTargetDepartmentId("");
      } catch (error) {
        setErrorMessage(
          error instanceof Error
            ? error.message
            : "Hedef bölümler yüklenirken hata oluştu."
        );
      }
    }

    loadTargetDepartments();
  }, [targetUniversityId]);

  useEffect(() => {
    async function loadSourceCourses() {
      if (sourceDepartmentId === "") {
        setSourceCourses([]);
        setSourceCourseId("");
        return;
      }

      try {
        setErrorMessage(null);

        const data = await getCourses({
          departmentId: sourceDepartmentId,
          limit: 100,
        });

        setSourceCourses(data.items);
        setSourceCourseId("");
      } catch (error) {
        setErrorMessage(
          error instanceof Error
            ? error.message
            : "Kaynak dersler yüklenirken hata oluştu."
        );
      }
    }

    loadSourceCourses();
  }, [sourceDepartmentId]);

  async function handleGetRecommendations() {
    if (sourceCourseId === "" || targetDepartmentId === "") {
      setErrorMessage("Öneri almak için kaynak ders ve hedef bölüm seçmelisin.");
      return;
    }

    try {
      setIsRecommendationLoading(true);
      setErrorMessage(null);
      setRecommendations([]);
      setTotalCandidates(0);

      const data = await getCourseRecommendations({
        sourceCourseId,
        targetDepartmentId,
        limit: 5,
      });

      setRecommendations(data.items);
      setTotalCandidates(data.total_candidates);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Ders önerileri alınırken hata oluştu."
      );
    } finally {
      setIsRecommendationLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="hero">
        <div>
          <p className="eyebrow">CourseMatch</p>
          <h1>Üniversiteler arası ders eşdeğerlik önerisi</h1>
          <p className="heroText">
            Kaynak dersi seç, hedef bölümü belirle ve sistemin önerdiği en iyi
            ders eşleşmelerini görüntüle.
          </p>
        </div>

        <div className="statusCard">
          <span className="statusDot" />
          <div>
            <strong>Backend bağlantısı</strong>
            <p>{isLoading ? "Kontrol ediliyor..." : "Hazır"}</p>
          </div>
        </div>
      </section>

      {errorMessage && <div className="alert">{errorMessage}</div>}

      <section className="grid">
        <div className="card">
          <div className="cardHeader">
            <span className="step">1</span>
            <div>
              <h2>Kaynak ders</h2>
              <p>Öğrencinin almak istediği muafiyet için mevcut ders.</p>
            </div>
          </div>

          <label>
            Kaynak üniversite
            <select
              value={sourceUniversityId}
              onChange={(event) =>
                setSourceUniversityId(
                  event.target.value === "" ? "" : Number(event.target.value)
                )
              }
            >
              <option value="">Üniversite seç</option>
              {universities.map((university) => (
                <option key={university.id} value={university.id}>
                  {university.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Kaynak bölüm
            <select
              value={sourceDepartmentId}
              disabled={sourceDepartments.length === 0}
              onChange={(event) =>
                setSourceDepartmentId(
                  event.target.value === "" ? "" : Number(event.target.value)
                )
              }
            >
              <option value="">Bölüm seç</option>
              {sourceDepartments.map((department) => (
                <option key={department.id} value={department.id}>
                  {department.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Kaynak ders
            <select
              value={sourceCourseId}
              disabled={sourceCourses.length === 0}
              onChange={(event) =>
                setSourceCourseId(
                  event.target.value === "" ? "" : Number(event.target.value)
                )
              }
            >
              <option value="">Ders seç</option>
              {sourceCourses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.code ? `${course.code} - ${course.name}` : course.name}
                </option>
              ))}
            </select>
          </label>

          {selectedSourceCourse && (
            <div className="coursePreview">
              <strong>{selectedSourceCourse.name}</strong>
              <span>
                AKTS: {selectedSourceCourse.ects ?? "-"} · Kredi:{" "}
                {selectedSourceCourse.credit ?? "-"}
              </span>
            </div>
          )}
        </div>

        <div className="card">
          <div className="cardHeader">
            <span className="step">2</span>
            <div>
              <h2>Hedef bölüm</h2>
              <p>Karşılaştırma yapılacak üniversite ve bölüm.</p>
            </div>
          </div>

          <label>
            Hedef üniversite
            <select
              value={targetUniversityId}
              onChange={(event) =>
                setTargetUniversityId(
                  event.target.value === "" ? "" : Number(event.target.value)
                )
              }
            >
              <option value="">Üniversite seç</option>
              {universities.map((university) => (
                <option key={university.id} value={university.id}>
                  {university.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Hedef bölüm
            <select
              value={targetDepartmentId}
              disabled={targetDepartments.length === 0}
              onChange={(event) =>
                setTargetDepartmentId(
                  event.target.value === "" ? "" : Number(event.target.value)
                )
              }
            >
              <option value="">Bölüm seç</option>
              {targetDepartments.map((department) => (
                <option key={department.id} value={department.id}>
                  {department.name}
                </option>
              ))}
            </select>
          </label>

          <button
            type="button"
            onClick={handleGetRecommendations}
            disabled={
              sourceCourseId === "" ||
              targetDepartmentId === "" ||
              isRecommendationLoading
            }
          >
            {isRecommendationLoading ? "Öneriler getiriliyor..." : "Önerileri getir"}
          </button>
        </div>
      </section>

      <section className="results">
        <div className="resultsHeader">
          <div>
            <h2>Önerilen ders eşleşmeleri</h2>
            <p>
              Toplam aday ders: <strong>{totalCandidates}</strong>
            </p>
          </div>
        </div>

        {recommendations.length === 0 ? (
          <div className="emptyState">
            Henüz öneri yok. Kaynak ders ve hedef bölüm seçip önerileri getir.
          </div>
        ) : (
          <div className="recommendationList">
            {recommendations.map((recommendation) => (
              <article
                key={recommendation.target_course_id}
                className="recommendationCard"
              >
                <div className="recommendationTop">
                  <div>
                    <h3>{recommendation.target_course_name}</h3>
                    <p>{recommendation.summary}</p>
                  </div>

                  <div className="score">
                    {recommendation.similarity_score.toFixed(1)}
                    <span>puan</span>
                  </div>
                </div>

                <div className="metaGrid">
                  <span>
                    Anahtar kelime skoru:{" "}
                    <strong>
                      {recommendation.keyword_similarity_score.toFixed(1)}
                    </strong>
                  </span>
                  <span>
                    AKTS:{" "}
                    <strong>
                      {recommendation.ects_match ? "Uyumlu" : "Farklı"}
                    </strong>
                  </span>
                  <span>
                    Kredi:{" "}
                    <strong>
                      {recommendation.credit_match ? "Uyumlu" : "Farklı"}
                    </strong>
                  </span>
                  <span>
                    Öneri: <strong>{recommendation.recommendation}</strong>
                  </span>
                </div>

                {recommendation.matched_keywords.length > 0 && (
                  <div className="keywords">
                    {recommendation.matched_keywords.map((keyword) => (
                      <span key={keyword}>{keyword}</span>
                    ))}
                  </div>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export default App;