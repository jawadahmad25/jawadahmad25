interface DataTableProps {
  columns: string[];
  data: Record<string, unknown>[];
  maxRows?: number;
}

export default function DataTable({ columns, data, maxRows = 100 }: DataTableProps) {
  const displayData = data.slice(0, maxRows);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-surface-200 dark:border-surface-700">
            {columns.map(col => (
              <th key={col} className="text-left py-2 px-3 font-medium text-surface-600 dark:text-surface-300 whitespace-nowrap">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {displayData.map((row, i) => (
            <tr key={i} className="border-b border-surface-100 dark:border-surface-800 hover:bg-surface-50 dark:hover:bg-surface-800/50">
              {columns.map(col => (
                <td key={col} className="py-2 px-3 text-surface-700 dark:text-surface-300 whitespace-nowrap font-mono text-xs">
                  {typeof row[col] === 'number' ? (row[col] as number).toFixed(4) : String(row[col] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length > maxRows && (
        <p className="text-xs text-surface-400 mt-2 text-center">
          Showing {maxRows} of {data.length} rows
        </p>
      )}
    </div>
  );
}
