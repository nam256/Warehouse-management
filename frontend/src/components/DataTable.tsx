
export default function DataTable({
  columns,
  rows,
}: {
  columns: { key: string; label: string }[];
  rows: Record<string, unknown>[];
}) {
  return (
    <table className="table">
      <thead>
        <tr>
          {columns.map((c) => (
            <th key={c.key}>{c.label}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i}>
            {columns.map((c) => (
              <td key={c.key}>{String(row[c.key] ?? "—")}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
