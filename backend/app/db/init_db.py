from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.database import SessionLocal, engine

# Model importları gerekli.
# Bu importlar olmadan SQLAlchemy tablo sınıflarını tanımaz.
from app.models import Course, CourseComparison, Department, University  # noqa: F401


def get_or_create_university(
    db: Session,
    name: str,
    city: str | None = None,
    country: str | None = None,
    website: str | None = None,
) -> University:
    university = db.query(University).filter(University.name == name).first()

    if university:
        return university

    university = University(
        name=name,
        city=city,
        country=country,
        website=website,
    )

    db.add(university)
    db.commit()
    db.refresh(university)

    return university


def get_or_create_department(
    db: Session,
    university_id: int,
    name: str,
    faculty: str | None = None,
) -> Department:
    department = (
        db.query(Department)
        .filter(
            Department.university_id == university_id,
            Department.name == name,
        )
        .first()
    )

    if department:
        return department

    department = Department(
        university_id=university_id,
        name=name,
        faculty=faculty,
    )

    db.add(department)
    db.commit()
    db.refresh(department)

    return department


def get_or_create_course(
    db: Session,
    department_id: int,
    code: str,
    name: str,
    language: str,
    ects: int,
    credit: int,
    description: str,
    weekly_plan: str,
    learning_outcomes: str,
    resources: str | None = None,
) -> Course:
    course = (
        db.query(Course)
        .filter(
            Course.department_id == department_id,
            Course.code == code,
        )
        .first()
    )

    if course:
        return course

    course = Course(
        department_id=department_id,
        code=code,
        name=name,
        language=language,
        ects=ects,
        credit=credit,
        description=description,
        weekly_plan=weekly_plan,
        learning_outcomes=learning_outcomes,
        resources=resources,
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


def seed_demo_data() -> None:
    db = SessionLocal()

    try:
        metu = get_or_create_university(
            db=db,
            name="Orta Doğu Teknik Üniversitesi",
            city="Ankara",
            country="Türkiye",
            website="https://www.metu.edu.tr",
        )

        itu = get_or_create_university(
            db=db,
            name="İstanbul Teknik Üniversitesi",
            city="İstanbul",
            country="Türkiye",
            website="https://www.itu.edu.tr",
        )

        bogazici = get_or_create_university(
            db=db,
            name="Boğaziçi Üniversitesi",
            city="İstanbul",
            country="Türkiye",
            website="https://www.boun.edu.tr",
        )

        metu_ceng = get_or_create_department(
            db=db,
            university_id=metu.id,
            name="Bilgisayar Mühendisliği",
            faculty="Mühendislik Fakültesi",
        )

        itu_ceng = get_or_create_department(
            db=db,
            university_id=itu.id,
            name="Bilgisayar Mühendisliği",
            faculty="Bilgisayar ve Bilişim Fakültesi",
        )

        bogazici_ceng = get_or_create_department(
            db=db,
            university_id=bogazici.id,
            name="Bilgisayar Mühendisliği",
            faculty="Mühendislik Fakültesi",
        )

        get_or_create_course(
            db=db,
            department_id=metu_ceng.id,
            code="CENG140",
            name="C Programlama",
            language="İngilizce",
            ects=6,
            credit=4,
            description=(
                "Programlama temelleri, algoritmik düşünme, değişkenler, "
                "kontrol yapıları, fonksiyonlar, diziler ve dosya işlemleri."
            ),
            weekly_plan=(
                "Algoritma kavramı, veri tipleri, koşullar, döngüler, "
                "fonksiyonlar, diziler, işaretçiler, dosya okuma yazma."
            ),
            learning_outcomes=(
                "Öğrenci temel programlama problemlerini analiz eder, "
                "C diliyle algoritma geliştirir ve kod yazar."
            ),
            resources="C Programming: A Modern Approach",
        )

        get_or_create_course(
            db=db,
            department_id=metu_ceng.id,
            code="CENG213",
            name="Veri Yapıları",
            language="İngilizce",
            ects=6,
            credit=4,
            description=(
                "Listeler, yığınlar, kuyruklar, ağaçlar, grafikler, "
                "hash tabloları ve temel algoritma analizi."
            ),
            weekly_plan=(
                "Bağlı listeler, stack, queue, binary tree, heap, graph, "
                "sorting, searching, complexity analysis."
            ),
            learning_outcomes=(
                "Öğrenci uygun veri yapısını seçer, algoritma karmaşıklığını "
                "analiz eder ve etkin çözümler geliştirir."
            ),
            resources="Data Structures and Algorithm Analysis",
        )

        get_or_create_course(
            db=db,
            department_id=itu_ceng.id,
            code="BLG102E",
            name="Introduction to Scientific and Engineering Computing",
            language="İngilizce",
            ects=6,
            credit=3,
            description=(
                "Programming fundamentals, algorithm design, variables, "
                "conditionals, loops, functions, arrays and file operations."
            ),
            weekly_plan=(
                "Problem solving, programming basics, control flow, loops, "
                "functions, lists, arrays, files and debugging."
            ),
            learning_outcomes=(
                "Students solve engineering problems using programming, "
                "algorithmic thinking and structured code."
            ),
            resources="Python and C programming notes",
        )

        get_or_create_course(
            db=db,
            department_id=itu_ceng.id,
            code="BLG223E",
            name="Data Structures",
            language="İngilizce",
            ects=6,
            credit=3,
            description=(
                "Fundamental data structures including linked lists, stacks, "
                "queues, trees, graphs and hashing."
            ),
            weekly_plan=(
                "Lists, stack, queue, recursion, trees, binary search trees, "
                "graphs, shortest paths, hashing and complexity."
            ),
            learning_outcomes=(
                "Students implement data structures and evaluate algorithmic "
                "efficiency for computational problems."
            ),
            resources="Data Structures in C",
        )

        get_or_create_course(
            db=db,
            department_id=bogazici_ceng.id,
            code="CMPE150",
            name="Introduction to Computing",
            language="İngilizce",
            ects=5,
            credit=3,
            description=(
                "Introduction to programming, computational thinking, "
                "problem solving, variables, conditionals, loops and functions."
            ),
            weekly_plan=(
                "Computer systems, algorithms, variables, expressions, "
                "conditionals, iteration, functions, arrays and file processing."
            ),
            learning_outcomes=(
                "Students design algorithms and implement basic programs "
                "for computational problem solving."
            ),
            resources="Introductory programming materials",
        )

        get_or_create_course(
            db=db,
            department_id=bogazici_ceng.id,
            code="CMPE250",
            name="Data Structures and Algorithms",
            language="İngilizce",
            ects=7,
            credit=4,
            description=(
                "Data structures, algorithmic analysis, lists, trees, heaps, "
                "graphs, sorting and searching algorithms."
            ),
            weekly_plan=(
                "Complexity analysis, abstract data types, linked lists, "
                "trees, heaps, graphs, sorting, searching and hashing."
            ),
            learning_outcomes=(
                "Students analyze algorithms and use data structures to "
                "solve software engineering problems efficiently."
            ),
            resources="Algorithms and Data Structures textbooks",
        )

    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    seed_demo_data()