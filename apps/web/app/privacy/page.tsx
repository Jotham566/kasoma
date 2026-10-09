import { Requests } from "./requests";
import { exportNotice } from "./export-notice";

export default async function Privacy({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const query = await searchParams;
  return <Requests exportNotice={exportNotice(query.export_error)} />;
}
