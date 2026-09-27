import type { DoctorQueueItem } from '../../api/episodes'

interface DoctorQueuePanelProps {
  clinicQueue: DoctorQueueItem[]
  wardQueue: DoctorQueueItem[]
  selectedEpisodeId: string | null
  onSelectQueueItem: (
    item: DoctorQueueItem,
    source: 'CLINIC' | 'WARD',
  ) => void
}

export default function DoctorQueuePanel({
  clinicQueue,
  wardQueue,
  selectedEpisodeId,
  onSelectQueueItem,
}: DoctorQueuePanelProps) {
  return (
    <section
      className={
        selectedEpisodeId
          ? 'workspace-panel doctor-queue-panel compact'
          : 'workspace-panel doctor-queue-panel'
      }
    >
      <details open={!selectedEpisodeId}>
        <summary className="doctor-queue-summary">
          <div>
            <p className="eyebrow">MY QUEUE</p>
            <h2>Doctor Queue</h2>
            <p>Patients currently requiring your attention.</p>
          </div>

          <span>
            {clinicQueue.length + wardQueue.length}
          </span>
        </summary>

        <div className="doctor-queue-sections">
          <div className="doctor-queue-section">
            <div className="doctor-queue-section-header">
              <strong>Clinic</strong>
              <span>{clinicQueue.length}</span>
            </div>

            {clinicQueue.length === 0 ? (
              <p className="doctor-queue-empty">
                No patients waiting for assessment.
              </p>
            ) : (
              <div className="doctor-queue-list">
                {clinicQueue.map(item => (
                  <button
                    key={item.id}
                    type="button"
                    className={
                      selectedEpisodeId === item.id
                        ? 'doctor-queue-item active'
                        : 'doctor-queue-item'
                    }
                    onClick={() =>
                      onSelectQueueItem(item, 'CLINIC')
                    }
                  >
                    <span>
                      <strong>{item.patient_name}</strong>
                      <small>{item.hospital_number}</small>
                    </span>

                    <small>{item.title}</small>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="doctor-queue-divider" />

          <div className="doctor-queue-section">
            <div className="doctor-queue-section-header">
              <strong>Ward</strong>
              <span>{wardQueue.length}</span>
            </div>

            {wardQueue.length === 0 ? (
              <p className="doctor-queue-empty">
                No admitted patients assigned to you.
              </p>
            ) : (
              <div className="doctor-queue-list">
                {wardQueue.map(item => (
                  <button
                    key={item.id}
                    type="button"
                    className={
                      selectedEpisodeId === item.id
                        ? 'doctor-queue-item active'
                        : 'doctor-queue-item'
                    }
                    onClick={() =>
                      onSelectQueueItem(item, 'WARD')
                    }
                  >
                    <span>
                      <strong>{item.patient_name}</strong>
                      <small>{item.hospital_number}</small>
                    </span>

                    <small>{item.title}</small>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </details>
    </section>
  )
}
