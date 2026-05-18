import { useEffect, useMemo, useState } from "react";

import {
  compareCourses,
  getComparisonHistory,
  getCourseRecommendations,
  getCourses,
  getDepartments,
  getUniversities,
} from "./api";
import type {
  Course,
  CourseComparisonHistoryItem,
  CourseRecommendationItem,
  Department,
  University,
} from "./types";

import "./App.css";

type RecommendationPresentation = {
  label: string;
  description: string;
  className: string;
};

const recommendationPresentationMap: Record<string, RecommendationPresentation> = {
  equivalent: {
    label: "Güçlü eşleşme",
    description: "Eşdeğerlik için güçlü aday.",
    className: "equivalent",
  },
  review_required: {
    label: "İnceleme gerekli",
    description: "Akademik kurul veya danışman kontrolü önerilir.",
    className: "reviewRequired",
  },
  not_equivalent: {
    label: "Zayıf eşleşme",
    description: "Eşdeğerlik ihtimali düşük görünüyor.",
    className: "notEquivalent",
  },
};

function getRecommendationPresentation(
  recommendation: string
): RecommendationPresentation {
  return (
    recommendationPresentationMap[recommendation] ?? {
      label: recommendation,
      description: "Sistem tarafından üretilen öneri sonucu.",
      className: "unknown",
    }
  );
}

function formatScore(score: number): string {
  return score.toFixed(1);
}

function formatDate(dateText: string): string {
  return new Intl.DateTimeFormat("tr-TR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(dateText));
}

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

  const [history, setHistory] = useState<CourseComparisonHistoryItem[]>([]);
  const [savedComparisonKeys, setSavedComparisonKeys] = useState<Set<string>>(
    new Set()
  );

  const [totalCandidates, setTotalCandidates] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecommendationLoading, setIsRecommendationLoading] = useState(false);
  const [savingTargetCourseId, setSavingTargetCourseId] = useState<number | null>(
    null
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const selectedSourceCourse = useMemo(() => {
    if (sourceCourseId === "") {
      return null;
    }

    return sourceCourses.find((course) => course.id === sourceCourseId) ?? null;
  }, [sourceCourseId, sourceCourses]);

  const hasEnoughSelection = sourceCourseId !== "" && targetDepartmentId !== "";

  function buildComparisonKey(sourceId: number, targetId: number): string {
    return `${sourceId}-${targetId}`;
  }

  function isComparisonSaved(sourceId: number, targetId: number): boolean {
    const key = buildComparisonKey(sourceId, targetId);

    return (
      savedComparisonKeys.has(key) ||
      history.some(
        (item) =>
          item.source_course_id === sourceId && item.target_course_id === targetId
      )
    );
  }

  async function loadHistory() {
    const data = await getComparisonHistory({
      limit: 5,
    });

    setHistory(data.items);
  }

  useEffect(() => {
    async function loadInitialData() {
      try {
        setIsLoading(true);
        setErrorMessage(null);

        const [universityData] = await Promise.all([
          getUniversities(),
          loadHistory(),
        ]);

        setUniversities(universityData);
      } catch (error) {
        setErrorMessage(
          error instanceof Error
            ? error.message
            : "Başlangıç verileri yüklenirken hata oluştu."
        );
      } finally {
        setIsLoading(false);
      }
    }

    loadInitialData();
  }, []);

  useEffect(() => {
    async function loadSourceDepartments() {
      if (sourceUniversityId === "") {
        setSourceDepartments([]);
        setSourceDepartmentId("");
        setSourceCourses([]);
        setSourceCourseId("");
        setRecommendations([]);
        setTotalCandidates(0);
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
        setRecommendations([]);
        setTotalCandidates(0);
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
        setRecommendations([]);
        setTotalCandidates(0);
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
        setRecommendations([]);
        setTotalCandidates(0);
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
        setRecommendations([]);
        setTotalCandidates(0);
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
        setRecommendations([]);
        setTotalCandidates(0);
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
      setSuccessMessage(null);
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

  async function handleSaveComparison(recommendation: CourseRecommendationItem) {
    if (sourceCourseId === "") {
      setErrorMessage("Karşılaştırmayı kaydetmek için kaynak ders seçmelisin.");
      return;
    }

    const comparisonKey = buildComparisonKey(
      sourceCourseId,
      recommendation.target_course_id
    );

    if (isComparisonSaved(sourceCourseId, recommendation.target_course_id)) {
      setSuccessMessage("Bu karşılaştırma zaten son kayıtlar içinde görünüyor.");
      return;
    }

    try {
      setSavingTargetCourseId(recommendation.target_course_id);
      setErrorMessage(null);
      setSuccessMessage(null);

      await compareCourses({
        sourceCourseId,
        targetCourseId: recommendation.target_course_id,
      });

      setSavedComparisonKeys((currentKeys) => {
        const nextKeys = new Set(currentKeys);
        nextKeys.add(comparisonKey);
        return nextKeys;
      });

      await loadHistory();

      setSuccessMessage("Karşılaştırma başarıyla kaydedildi.");
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Karşılaştırma kaydedilirken hata oluştu."
      );
    } finally {
      setSavingTargetCourseId(null);
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
            ders eşleşmelerini açıklamalı skorlarla görüntüle.
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
      {successMessage && <div className="success">{successMessage}</div>}

      <section className="grid">
        <div className="card">
          <div className="cardHeader">
            <span className="step">1</span>
            <div>
              <h2>Kaynak ders</h2>
              <p>Öğrencinin muafiyet almak istediği mevcut ders.</p>
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
              {selectedSourceCourse.description && (
                <p>{selectedSourceCourse.description}</p>
              )}
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
            disabled={!hasEnoughSelection || isRecommendationLoading}
          >
            {isRecommendationLoading ? "Öneriler getiriliyor..." : "Önerileri getir"}
          </button>

          <div className="selectionHint">
            <strong>Nasıl hesaplanıyor?</strong>
            <p>
              Sistem ders içeriklerinden ortak anahtar kelimeleri çıkarır; AKTS
              ve kredi uyumunu ek puan olarak değerlendirir.
            </p>
          </div>
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
            {recommendations.map((recommendation, index) => {
              const presentation = getRecommendationPresentation(
                recommendation.recommendation
              );

              const saved =
                sourceCourseId !== "" &&
                isComparisonSaved(sourceCourseId, recommendation.target_course_id);

              return (
                <article
                  key={recommendation.target_course_id}
                  className={`recommendationCard ${presentation.className}`}
                >
                  <div className="recommendationTop">
                    <div>
                      <div className="recommendationTitleRow">
                        <span className="rankBadge">#{index + 1}</span>
                        <h3>{recommendation.target_course_name}</h3>
                      </div>

                      <div className={`decisionBadge ${presentation.className}`}>
                        {presentation.label}
                      </div>

                      <p>{recommendation.summary}</p>
                      <small>{presentation.description}</small>
                    </div>

                    <div className="score">
                      {formatScore(recommendation.similarity_score)}
                      <span>puan</span>
                    </div>
                  </div>

                  <div className="scoreBreakdown">
                    <div>
                      <span>Anahtar kelime skoru</span>
                      <strong>
                        {formatScore(recommendation.keyword_similarity_score)}
                      </strong>
                    </div>

                    <div>
                      <span>AKTS uyumu</span>
                      <strong
                        className={
                          recommendation.ects_match ? "positive" : "negative"
                        }
                      >
                        {recommendation.ects_match ? "Uyumlu" : "Farklı"}
                      </strong>
                    </div>

                    <div>
                      <span>Kredi uyumu</span>
                      <strong
                        className={
                          recommendation.credit_match ? "positive" : "negative"
                        }
                      >
                        {recommendation.credit_match ? "Uyumlu" : "Farklı"}
                      </strong>
                    </div>

                    <div>
                      <span>Karar</span>
                      <strong>{presentation.label}</strong>
                    </div>
                  </div>

                  <div className="scoreBar">
                    <span
                      style={{
                        width: `${Math.min(
                          Math.max(recommendation.similarity_score, 0),
                          100
                        )}%`,
                      }}
                    />
                  </div>

                  {recommendation.matched_keywords.length > 0 ? (
                    <div className="keywords">
                      {recommendation.matched_keywords.map((keyword) => (
                        <span key={keyword}>{keyword}</span>
                      ))}
                    </div>
                  ) : (
                    <p className="noKeywordText">
                      Ortak anahtar kelime bulunamadı.
                    </p>
                  )}

                  <div className="recommendationActions">
                    <button
                      className="saveButton"
                      type="button"
                      disabled={saved || savingTargetCourseId === recommendation.target_course_id}
                      onClick={() => handleSaveComparison(recommendation)}
                    >
                      {savingTargetCourseId === recommendation.target_course_id
                        ? "Kaydediliyor..."
                        : saved
                          ? "Kaydedildi"
                          : "Karşılaştırmayı kaydet"}
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <section className="historySection">
        <div className="resultsHeader">
          <div>
            <h2>Son karşılaştırmalar</h2>
            <p>Kaydedilen son eşdeğerlik karşılaştırmaları.</p>
          </div>

          <button className="refreshButton" type="button" onClick={loadHistory}>
            Geçmişi yenile
          </button>
        </div>

        {history.length === 0 ? (
          <div className="emptyState">
            Henüz kaydedilmiş karşılaştırma yok.
          </div>
        ) : (
          <div className="historyList">
            {history.map((item) => {
              const presentation = getRecommendationPresentation(
                item.recommendation
              );

              return (
                <article key={item.id} className="historyItem">
                  <div>
                    <div className="historyTitle">
                      <strong>{item.source_course_name}</strong>
                      <span>↔</span>
                      <strong>{item.target_course_name}</strong>
                    </div>

                    <p>{item.summary}</p>

                    <div className="historyMeta">
                      <span>{formatDate(item.created_at)}</span>
                      <span className={`decisionBadge small ${presentation.className}`}>
                        {presentation.label}
                      </span>
                    </div>
                  </div>

                  <div className="historyScore">
                    {formatScore(item.similarity_score)}
                    <span>puan</span>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </main>
  );
}

export default App;