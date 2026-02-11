import React from "react";

function Recommendations({ recommendations }) {
  if (!recommendations || !recommendations.length) return null;
  return (
    <div className="mt-4">
      <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2 flex items-center gap-2">
        <span className="text-teal-500" aria-hidden>●</span>
        Recommendations
      </h3>
      <ul className="list-disc list-outside pl-5 space-y-2 text-sm text-gray-700 dark:text-gray-300">
        {recommendations.map((rec, i) => (
          <li key={i} className="pl-0.5">{rec}</li>
        ))}
      </ul>
    </div>
  );
}

function MissingKeywords({ missing_keywords, missing_keywords_by_category }) {
  const byCategory = missing_keywords_by_category || {};
  const flat = missing_keywords || [];
  if (flat.length === 0) return null;

  const hasCategories = Object.keys(byCategory).length > 0;
  return (
    <div className="mt-4">
      <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2 flex items-center gap-2">
        <span className="text-indigo-500" aria-hidden>●</span>
        Missing keywords from job description
      </h3>
      {hasCategories ? (
        <ul className="list-disc list-outside pl-5 space-y-2 text-sm text-gray-700 dark:text-gray-300">
          {Object.entries(byCategory).map(([category, kws]) => (
            <li key={category} className="pl-0.5">
              <span className="font-medium text-gray-600 dark:text-gray-400">{category}:</span>{" "}
              <span>{kws.join(", ")}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-gray-700 dark:text-gray-300 pl-5">
          {flat.join(", ")}
        </p>
      )}
    </div>
  );
}

function SectionScores({ section_scores }) {
  if (!section_scores || !Object.keys(section_scores).length) return null;
  const entries = Object.entries(section_scores).map(([name, val]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value: Math.round((val || 0) * 100),
  }));
  return (
    <div className="mt-4">
      <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2 flex items-center gap-2">
        <span className="text-violet-500" aria-hidden>●</span>
        Section match (vs job description)
      </h3>
      <ul className="list-disc list-outside pl-5 space-y-2 text-sm text-gray-700 dark:text-gray-300">
        {entries.map(({ name, value }) => (
          <li key={name} className="pl-0.5">
            <span className="font-medium text-gray-600 dark:text-gray-400">{name}:</span> {value}%
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function InsightsPanel({
  recommendations,
  missing_keywords,
  missing_keywords_by_category,
  section_scores,
}) {
  const hasRecs = recommendations && recommendations.length > 0;
  const hasMissing = missing_keywords && missing_keywords.length > 0;
  const hasSections = section_scores && Object.keys(section_scores).length > 0;
  if (!hasRecs && !hasMissing && !hasSections) return null;

  return (
    <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-600 text-left w-full">
      <Recommendations recommendations={recommendations} />
      <MissingKeywords
        missing_keywords={missing_keywords}
        missing_keywords_by_category={missing_keywords_by_category}
      />
      <SectionScores section_scores={section_scores} />
    </div>
  );
}
