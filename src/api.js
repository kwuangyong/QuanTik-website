// Tất cả lời gọi tới phần Python nằm ở đây. Đổi VITE_API_BASE khi deploy.
const BASE = import.meta.env.VITE_API_BASE ?? '/api';

async function j(res) {
  if (!res.ok) {
    let detail;try{detail=(await res.json()).detail;}catch{}
    const error=new Error(typeof detail==='string'?detail:`Dịch vụ báo lỗi HTTP ${res.status}.`);
    error.status=res.status;throw error;
  }
  return res.json();
}

/** Snapshot bảng điện: metadata/units/instruments/sectors/quotes; giá VND. */
export const getBoard = (group = 'ALL', signal) => fetch(`${BASE}/board?group=${encodeURIComponent(group)}`, {signal}).then(j);

/** Bắt đầu chạy quant cho 1 mã. modules = null nghĩa là chạy tất cả. */
export const startQuant = (symbol, modules = null) =>
  fetch(`${BASE}/quant/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, modules }),
  }).then(j);

/** {id,status:'queued|running|done|error',modules:[{id,name,state,sec}],summary,error} */
export const getJob = (id) => fetch(`${BASE}/quant/jobs/${id}`).then(j);

/** Ảnh tổng quan bổ sung từ adapter backend. */
export const jobImageUrl = (id) => `${BASE}/quant/jobs/${id}/image`;

export const listModules = () => fetch(`${BASE}/quant/modules`).then(j);

/** Read the last published scan; this GET never starts a quant job. */
export const getLatestScan = (signal) => fetch(`${BASE}/scan/latest`, {signal, cache:'no-store'}).then(j);

/** Read only server-selected 5/5 from a single pinned publication. */
export const getScanHighlights = async signal => {
 const response=await fetch(`${BASE}/scan/latest/highlights`, {signal,cache:'no-store'});
 // Compatibility with the previous read-only backend; never fall back on 503.
 return response.status===404?getLatestScan(signal):j(response);
};
