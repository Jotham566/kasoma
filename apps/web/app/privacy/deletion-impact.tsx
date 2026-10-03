import type { components } from "@kasoma/api-client";

type Preview = components["schemas"]["DeletionPreview"];
const policies: Record<Preview["sources"][number]["retention"], string> = {
  REMOVE_DIRECT_LINKAGE: "Remove direct account linkage during processing",
  ANONYMIZATION_REVIEW: "Anonymization and re-identification review required",
  SIX_YEARS_AFTER_CLOSURE_OR_WITHDRAWAL:
    "Six years after closure or withdrawal; subject to record-specific legal holds",
  SIX_YEARS_AFTER_COMPLETION: "Six years after request completion",
  TWENTY_FOUR_MONTHS_AFTER_RESOLUTION: "24 months after resolution",
  EXPIRES_AFTER_24_HOURS: "Copy expires 24 hours after generation",
  STAFF_PROVENANCE_REVIEW:
    "Separate review of staff and other people's records",
  TRANSIENT_EXPIRY: "Existing short-lived verification expiry policy",
};
const blockers: Record<Preview["blockers"][number], string> = {
  LEGAL_HOLD_COVERAGE_INCOMPLETE:
    "Legal holds cover four record types; other records still require review.",
  ACTIVE_RECORD_HOLDS:
    "Active holds preserve specific records; they do not hold the whole account.",
  LEGAL_HOLD_CHECK_UNAVAILABLE:
    "Record-specific legal holds have not been checked.",
  ERASURE_PROCESSOR_UNAVAILABLE: "The deletion processor is not implemented.",
  ANONYMIZATION_REVIEW_REQUIRED:
    "Permitted evidence and re-identification risks need review.",
  STAFF_RECORDS_REQUIRE_REVIEW:
    "This account has staff-related records requiring separate review.",
};

export function DeletionImpact({ preview }: { preview: Preview }) {
  return (
    <section
      className="space-y-3 rounded border border-slate-500 p-4"
      aria-labelledby="deletion-impact-title"
    >
      <h2 id="deletion-impact-title" className="text-xl font-semibold">
        Deletion impact preview
      </h2>
      <p>Reference: {preview.request_id}</p>
      <p>
        Active registered holds: {preview.active_legal_holds ?? 0}
        {preview.active_holds_at_least ? "+" : ""}
      </p>
      <p>
        No deletion is enabled. This preview does not revoke access, remove
        records or complete the request.
      </p>
      <p>
        Observed:{" "}
        {new Date(preview.observed_at).toLocaleString("en-GB", {
          timeZone: "Africa/Kampala",
        })}{" "}
        (Kampala). Counts may change and related categories can overlap.
      </p>
      <ul className="list-disc pl-5">
        {preview.blockers.map((code) => (
          <li key={code}>{blockers[code]}</li>
        ))}
      </ul>
      <details>
        <summary className="min-h-11 cursor-pointer py-2">
          Record counts and retention
        </summary>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <caption className="py-2 text-left">
              Known linked records; counts marked + are lower bounds.
            </caption>
            <thead>
              <tr>
                <th scope="col" className="p-2">
                  Records
                </th>
                <th scope="col" className="p-2">
                  Count
                </th>
                <th scope="col" className="p-2">
                  Retention or review
                </th>
              </tr>
            </thead>
            <tbody>
              {preview.sources.map((source) => (
                <tr key={`${source.source}-${source.retention}`}>
                  <th scope="row" className="p-2 font-normal capitalize">
                    {source.source.replaceAll("_", " ")}
                  </th>
                  <td className="p-2">
                    {source.count}
                    {source.at_least ? "+" : ""}
                  </td>
                  <td className="p-2">{policies[source.retention]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
      <ul className="list-disc pl-5">
        {preview.limitations.map((text) => (
          <li key={text}>{text}</li>
        ))}
      </ul>
    </section>
  );
}
