// src/components/ui/Tag.jsx
export function Tag({ children }) {
  return <span className="tag">{children}</span>;
}

export function StatusTag({ status }) {
  return <span className={`tag status-${status}`}>{status}</span>;
}