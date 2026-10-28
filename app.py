
import ast
from collections import Counter
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Job Market Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Job Market Analyzer")
st.write(
    "Analyze historical and live job postings, in-demand skills, "
    "companies, locations, employment types, and salary information."
)


# ---------------- CONSTANTS ----------------

DATA_DIR = Path("data")

HISTORICAL_FILE = DATA_DIR / "jobs_with_skills_sample.csv"
LIVE_FILE = DATA_DIR / "live_jobs_processed.csv"

LIVE_SOURCE_NAME = "Live Job Market Analyzer"


# ---------------- DATA LOADING ----------------

@st.cache_data
def load_data(source):
    file_path = (
        HISTORICAL_FILE
        if source == "Historical Dataset"
        else LIVE_FILE
    )

    if not file_path.exists():
        raise FileNotFoundError(str(file_path))

    df = pd.read_csv(file_path, low_memory=False)

    # Standardize column names and ensure expected columns exist.
    optional_columns = [
        "title",
        "company_name",
        "location",
        "formatted_experience_level",
        "formatted_work_type",
        "normalized_salary",
        "remote_allowed",
        "contract_type",
        "contract_time",
        "salary_min",
        "salary_max",
        "job_url",
        "source",
        "extracted_skills",
        "description",
        "job_publisher",
        "search_keyword",
    ]

    for column in optional_columns:
        if column not in df.columns:
            df[column] = pd.NA

    # Parse extracted skills stored as lists in CSV strings.
    def parse_skills(value):
        if isinstance(value, list):
            return [
                str(skill).strip()
                for skill in value
                if str(skill).strip()
            ]

        if not isinstance(value, str) or not value.strip():
            return []

        try:
            result = ast.literal_eval(value)

            if isinstance(result, list):
                return [
                    str(skill).strip()
                    for skill in result
                    if str(skill).strip()
                ]

            return []
        except (ValueError, SyntaxError):
            return []

    df["extracted_skills"] = df["extracted_skills"].apply(
        parse_skills
    )

    # Clean text fields without changing missing values into "nan".
    text_columns = [
        "title",
        "company_name",
        "location",
        "formatted_experience_level",
        "formatted_work_type",
        "contract_type",
        "contract_time",
        "source",
        "job_url",
        "job_publisher",
        "search_keyword",
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].replace("", pd.NA)

    # Convert salary values to numeric where possible.
    for column in [
        "normalized_salary",
        "salary_min",
        "salary_max",
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


# ---------------- SOURCE SELECTOR ----------------

st.sidebar.header("Data Source")

source = st.sidebar.radio(
    "Choose job data",
    [
        "Historical Dataset",
        LIVE_SOURCE_NAME,
    ],
)

try:
    df = load_data(source)

except FileNotFoundError as error:
    st.error(
        f"Dataset not found: {error}. "
        "Check that the required CSV file exists in the data folder."
    )
    st.stop()

except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
    st.error(f"Could not read the dataset: {error}")
    st.stop()

if source == "Historical Dataset":
    st.caption(
        "Historical analysis using the downloaded dataset. "
        "These records may not represent currently available vacancies."
    )
else:
    st.caption(
        "Combined live listings from Adzuna, selected Greenhouse "
        "company boards, and JSearch. Listings may expire or change. "
        "Verify vacancies on the original job application page."
    )

if df.empty:
    st.warning("The selected dataset contains no job postings.")
    st.stop()


# ---------------- FILTERS ----------------

st.sidebar.header("Job Filters")
st.sidebar.caption(
    "Use the filters below to narrow down the matching job postings."
)

filtered_df = df.copy()


# Platform filter
if source == LIVE_SOURCE_NAME:
    available_sources = sorted(
        df["source"].dropna().astype(str).unique().tolist()
    )

    if available_sources:
        selected_sources = st.sidebar.multiselect(
            "Job Platform",
            options=available_sources,
            default=available_sources,
        )

        if selected_sources:
            filtered_df = filtered_df[
                filtered_df["source"].isin(selected_sources)
            ]
        else:
            filtered_df = filtered_df.iloc[0:0]


# Job title search
title_search = st.sidebar.text_input(
    "Search Job Title",
    placeholder="e.g. Data Analyst"
)

if title_search.strip():
    filtered_df = filtered_df[
        filtered_df["title"].str.contains(
            title_search.strip(),
            case=False,
            na=False,
            regex=False,
        )
    ]


# Experience level filter
experience_options = sorted(
    df["formatted_experience_level"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

if experience_options:
    selected_experience = st.sidebar.multiselect(
        "Experience Level",
        options=experience_options,
    )

    if selected_experience:
        filtered_df = filtered_df[
            filtered_df["formatted_experience_level"].isin(
                selected_experience
            )
        ]
else:
    st.sidebar.caption(
        "Experience-level information is unavailable."
    )


# Location search
location_search = st.sidebar.text_input(
    "Search Location",
    placeholder="e.g. Mumbai, India, Remote"
)

if location_search.strip():
    filtered_df = filtered_df[
        filtered_df["location"].str.contains(
            location_search.strip(),
            case=False,
            na=False,
            regex=False,
        )
    ]


# Employment type filter
if source == LIVE_SOURCE_NAME:
    work_columns = [
        column
        for column in ["contract_type", "contract_time"]
        if df[column].notna().any()
    ]

    if work_columns:
        work_column = st.sidebar.selectbox(
            "Employment Field",
            options=work_columns,
            format_func=lambda column: (
                "Employment Type"
                if column == "contract_type"
                else "Contract Time"
            ),
        )

        work_options = sorted(
            df[work_column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if work_options:
            selected_work = st.sidebar.multiselect(
                "Employment Type / Contract Time",
                options=work_options,
            )

            if selected_work:
                filtered_df = filtered_df[
                    filtered_df[work_column].isin(selected_work)
                ]

else:
    work_options = sorted(
        df["formatted_work_type"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if work_options:
        selected_work = st.sidebar.multiselect(
            "Work Type",
            options=work_options,
        )

        if selected_work:
            filtered_df = filtered_df[
                filtered_df["formatted_work_type"].isin(
                    selected_work
                )
            ]


# Company search
company_search = st.sidebar.text_input(
    "Search Company",
    placeholder="Enter a company name"
)

if company_search.strip():
    filtered_df = filtered_df[
        filtered_df["company_name"].str.contains(
            company_search.strip(),
            case=False,
            na=False,
            regex=False,
        )
    ]


# Remote filter
if "remote_allowed" in df.columns:
    remote_values = df["remote_allowed"].dropna()

    if not remote_values.empty:
        normalized_remote = (
            remote_values.astype(str).str.strip().str.lower()
        )

        if normalized_remote.isin(
            ["true", "false", "yes", "no", "1", "0"]
        ).any():
            remote_filter = st.sidebar.selectbox(
                "Remote Status",
                [
                    "All",
                    "Remote",
                    "Not marked remote",
                ],
            )

            remote_text = (
                df["remote_allowed"]
                .astype("string")
                .str.strip()
                .str.lower()
            )

            if remote_filter == "Remote":
                filtered_df = filtered_df[
                    remote_text.isin(["true", "yes", "1"])
                ]
            elif remote_filter == "Not marked remote":
                filtered_df = filtered_df[
                    remote_text.isin(["false", "no", "0"])
                ]


# ---------------- OVERVIEW METRICS ----------------

st.divider()
st.subheader("📌 Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Job Postings",
    f"{len(filtered_df):,}",
)

col2.metric(
    "Companies",
    f"{filtered_df['company_name'].nunique():,}",
)

col3.metric(
    "Unique Job Titles",
    f"{filtered_df['title'].nunique():,}",
)

salary_count = filtered_df["normalized_salary"].notna().sum()

col4.metric(
    "Normalized Salary Records",
    f"{salary_count:,}",
)


# Platform summary
if source == LIVE_SOURCE_NAME:
    st.subheader("Postings by Job Platform")

    platform_counts = (
        filtered_df["source"]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("Platform")
        .reset_index(name="Postings")
    )

    if not platform_counts.empty:
        st.dataframe(
            platform_counts,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No platform data matches the selected filters.")


# ---------------- JOB TITLE CHART ----------------

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Most Common Job Titles")

    titles = filtered_df["title"].dropna()
    titles = titles[titles.str.strip() != ""]

    if not titles.empty:
        top_titles = (
            titles.value_counts()
            .head(10)
            .rename_axis("Job Title")
            .reset_index(name="Postings")
        )

        fig = px.bar(
            top_titles.sort_values("Postings"),
            x="Postings",
            y="Job Title",
            orientation="h",
            title="Top 10 Job Titles",
            hover_data=["Postings"],
        )

        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            xaxis_title="Number of Postings",
            yaxis_title="",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": True,
            },
        )
    else:
        st.info("No matching job titles.")


# ---------------- EXPERIENCE CHART ----------------

with right:
    st.subheader("Experience Level Distribution")

    exp = (
        filtered_df["formatted_experience_level"]
        .dropna()
        .astype(str)
    )

    if not exp.empty:
        exp_counts = (
            exp.value_counts()
            .rename_axis("Experience Level")
            .reset_index(name="Postings")
        )

        fig = px.bar(
            exp_counts,
            x="Experience Level",
            y="Postings",
            title="Postings by Experience Level",
            hover_data=["Postings"],
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": True,
            },
        )
    else:
        st.info(
            "Experience-level information is unavailable "
            "for the selected records."
        )


# ---------------- IN-DEMAND SKILLS ----------------

st.divider()
st.subheader("🔥 In-Demand Skills")

skill_counts = Counter()

for skill_list in filtered_df["extracted_skills"]:
    if isinstance(skill_list, list):
        skill_counts.update(
            skill.strip().lower()
            for skill in skill_list
            if isinstance(skill, str) and skill.strip()
        )

if skill_counts:
    skills = pd.DataFrame(
        skill_counts.most_common(15),
        columns=["Skill", "Postings"],
    )

    fig = px.bar(
        skills.sort_values("Postings"),
        x="Postings",
        y="Skill",
        orientation="h",
        title="Top 15 Skills Mentioned in Job Descriptions",
        hover_data=["Postings"],
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="Skill Mentions",
        yaxis_title="",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": True,
        },
    )

    st.caption(
        "Counts reflect skills extracted by your current skill dictionary "
        "and extraction process. They represent mentions in the collected "
        "postings, not the entire job market or hiring probability."
    )
else:
    st.info(
        "No extracted skills found. Run the live processing script "
        "and check the skill extraction configuration."
    )


# ---------------- LOCATION CHART ----------------

st.divider()
st.subheader("📍 Top Hiring Locations")

locations = filtered_df["location"].dropna().astype(str)

locations = locations[
    (locations.str.strip() != "")
    & (locations.str.lower() != "unknown")
    & (locations.str.lower() != "nan")
]

if not locations.empty:
    location_counts = (
        locations.value_counts()
        .head(10)
        .rename_axis("Location")
        .reset_index(name="Postings")
    )

    fig = px.bar(
        location_counts.sort_values("Postings"),
        x="Postings",
        y="Location",
        orientation="h",
        title="Top 10 Locations",
        hover_data=["Postings"],
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="Number of Postings",
        yaxis_title="",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": True,
        },
    )
else:
    st.info("Location information is unavailable.")


# ---------------- SALARY ANALYSIS ----------------

st.divider()
st.subheader("💰 Salary Overview")

salary_data = filtered_df.dropna(
    subset=["normalized_salary"]
).copy()

if not salary_data.empty:
    fig = px.histogram(
        salary_data,
        x="normalized_salary",
        nbins=30,
        title="Distribution of Available Normalized Salaries",
        labels={
            "normalized_salary": "Normalized Salary",
        },
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": True,
        },
    )

    median_salary = salary_data["normalized_salary"].median()

    st.metric(
        "Median Normalized Salary",
        f"{median_salary:,.2f}",
    )

    st.caption(
        "Confirm the salary currency, pay period, and normalization "
        "method before comparing salary amounts."
    )

elif source == LIVE_SOURCE_NAME:
    st.info(
        "No comparable normalized salary data is available for the "
        "selected live postings. Raw salary fields may use different "
        "currencies or pay periods."
    )

else:
    st.info("No salary records match the selected filters.")


# ---------------- JOB TABLE ----------------

st.divider()
st.subheader("🔎 Explore Matching Jobs")

display_columns = [
    column
    for column in [
        "title",
        "company_name",
        "location",
        "source",
        "formatted_experience_level",
        "formatted_work_type",
        "contract_type",
        "contract_time",
        "salary_min",
        "salary_max",
        "job_url",
    ]
    if column in filtered_df.columns
]

if not filtered_df.empty:
    st.dataframe(
        filtered_df[display_columns].head(100),
        use_container_width=True,
        hide_index=True,
        column_config={
            "job_url": st.column_config.LinkColumn(
                "Apply / View Job",
                display_text="Open Job",
            ),
        },
    )

    st.caption("Showing up to 100 matching job records.")

else:
    st.info("No jobs match the selected filters.")


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "The analyzer uses collected historical and live job-posting samples. "
    "Coverage depends on the connected APIs and selected company boards. "
    "Posting counts and skill frequencies should not be interpreted as "
    "a complete representation of the job market."
)
