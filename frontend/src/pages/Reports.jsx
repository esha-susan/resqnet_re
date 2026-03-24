// frontend/src/pages/Reports.jsx
// Reports page — shows all generated incident reports.
// Each report is auto-generated when an incident is closed.

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import PriorityBadge from '../components/PriorityBadge'
import { fetchReports } from '../api/index'
import '../styles/reports.css'

function Reports() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)
  const navigate = useNavigate()

  useEffect(() => { loadReports() }, [])

  const loadReports = async () => {
    try {
      setLoading(true)
      const data = await fetchReports()
      setReports(data)
      if (data.length > 0) setSelected(data[0])
    } catch {
      console.error('Failed to load reports')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (iso) => {
    if (!iso) return 'Unknown'
    return new Date(iso).toLocaleString()
  }

  const rd = selected?.report_data

  return (
    <div>
      <Navbar />
      <div className="reports-container">

        <div className="reports-header">
          <h2>Incident Reports</h2>
          <p className="section-sub">
            Auto-generated reports for all closed incidents
          </p>
        </div>

        {loading ? (
          <div className="loading-state">Loading reports...</div>
        ) : reports.length === 0 ? (
          <div className="empty-state">
            <p>No reports yet.</p>
            <p>Reports are generated automatically when incidents are closed.</p>
          </div>
        ) : (
          <div className="reports-layout">

            {/* ── Report List (left) ── */}
            <div className="reports-list">
              {reports.map(report => (
                <div
                  key={report.id}
                  className={`report-item ${selected?.id === report.id ? 'active' : ''}`}
                  onClick={() => setSelected(report)}
                >
                  <div className="report-item-title">
                    {report.report_data?.incident?.title || 'Untitled'}
                  </div>
                  <div className="report-item-meta">
                    <PriorityBadge
                      priority={report.report_data?.incident?.priority}
                    />
                    <span className="report-item-date">
                      {formatDate(report.created_at)}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* ── Report Detail (right) ── */}
            {selected && rd && (
              <div className="report-detail">

                {/* ── Title ── */}
                <div className="rd-header">
                  <div className="rd-title-row">
                    <h3>{rd.incident?.title}</h3>
                    <PriorityBadge priority={rd.incident?.priority} />
                  </div>
                  <p className="rd-location">{rd.incident?.location}</p>
                  <p className="rd-description">{rd.incident?.description}</p>
                </div>

                {/* ── Timeline ── */}
                <div className="rd-section">
                  <h4>Timeline</h4>
                  <div className="rd-timeline">
                    <div className="rd-timeline-item">
                      <span className="rd-tl-label">Reported</span>
                      <span className="rd-tl-value">
                        {formatDate(rd.timeline?.reported)}
                      </span>
                    </div>
                    <div className="rd-timeline-item">
                      <span className="rd-tl-label">Closed</span>
                      <span className="rd-tl-value">
                        {formatDate(rd.timeline?.closed)}
                      </span>
                    </div>
                    <div className="rd-timeline-item highlight">
                      <span className="rd-tl-label">Total Response Time</span>
                      <span className="rd-tl-value">
                        {rd.timeline?.total_response_time}
                      </span>
                    </div>
                  </div>
                </div>

                {/* ── Resources ── */}
                <div className="rd-section">
                  <h4>Resources Deployed</h4>
                  <div className="rd-resource-summary">
                    <div className="rd-resource-total">
                      <span className="rd-big-number">
                        {rd.resources?.total_deployed}
                      </span>
                      <span className="rd-big-label">Total Units</span>
                    </div>
                    <div className="rd-resource-breakdown">
                      {Object.entries(
                        rd.resources?.breakdown || {}
                      ).map(([type, count]) => (
                        <div key={type} className="rd-resource-row">
                          <span>{type.replace('_', ' ')}</span>
                          <span className="rd-resource-count">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* ── Call Summary ── */}
                <div className="rd-section">
                  <h4>Responder Calls</h4>
                  <div className="rd-call-summary">
                    {[
                      {
                        label: 'Total Calls',
                        value: rd.calls?.summary?.total,
                        cls: ''
                      },
                      {
                        label: 'Confirmed',
                        value: rd.calls?.summary?.confirmed,
                        cls: 'green'
                      },
                      {
                        label: 'Unavailable',
                        value: rd.calls?.summary?.unavailable,
                        cls: 'red'
                      },
                      {
                        label: 'No Answer',
                        value: rd.calls?.summary?.no_answer,
                        cls: 'orange'
                      },
                    ].map(item => (
                      <div key={item.label} className="rd-call-stat">
                        <span className={`rd-call-num ${item.cls}`}>
                          {item.value ?? 0}
                        </span>
                        <span className="rd-call-label">{item.label}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* ── Resolution Summary ── */}
                <div className="rd-section">
                  <h4>Resolution Summary</h4>
                  <p className="rd-summary-text">
                    {rd.resolution_summary}
                  </p>
                </div>

                {/* ── Generated At ── */}
                <div className="rd-footer">
                  Report generated: {formatDate(rd.generated_at)}
                </div>

              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default Reports