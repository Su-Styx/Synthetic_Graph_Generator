export function Tag({ children }) {
  return <span className="tag">{children}</span>;
}

export function StatusTag({ status }) {
  if (status === 'completed') {
    return <span className={`tag status-${status}`} style={{ backgroundColor: 'rgb(131, 233, 131)', color: 'black' }}>
      {status}
    </span>;
  }

  if (status === 'failed') {
    return <span className={`tag status-${status}`} style={{ backgroundColor: 'rgb(252, 102, 102)', color: 'black' }}>
      {status}
    </span>;
  }
  if (status === 'running') {
    return <span className={`tag status-${status}`} style={{ backgroundColor: 'rgb(236, 236, 112)',color: 'black' }}>
      {status}
    </span>;
  }
  else {
      return <span className={`tag status-${status}`}>{status}</span>;
  }
  // return <span className={`tag status-${status}`}>{status}</span>;
}