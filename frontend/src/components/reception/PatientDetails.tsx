import type { Patient } from '../../types'
import type { Episode } from '../../api'


interface Props {
  patient: Patient
  episodes: Episode[]
  episodeLoading: boolean
  episodeError: string | null
  episodeActionLoading: boolean
  hasActiveEpisode: () => boolean
  onClose: () => void
  onStartVisit: () => void
  onCheckIn: (episode: Episode) => void
}


export default function PatientDetails({
  patient,
  episodes,
  episodeLoading,
  episodeError,
  episodeActionLoading,
  hasActiveEpisode,
  onClose,
  onStartVisit,
  onCheckIn,
}: Props) {
  return (
    <div className="patient-detail-card">

      <div className="detail-header">

        <div>
          <p className="eyebrow">
            PATIENT
          </p>

          <h2>
            {patient.first_name}{' '}
            {patient.last_name}
          </h2>

          <span>
            {patient.hospital_number}
          </span>
        </div>

        <button
          type="button"
          className="close-button"
          onClick={onClose}
        >
          Close
        </button>

      </div>


      <div className="detail-grid">

        <div>
          <span>Sex</span>
          <strong>
            {patient.sex}
          </strong>
        </div>

        <div>
          <span>Date of birth</span>
          <strong>
            {patient.date_of_birth}
          </strong>
        </div>

        <div>
          <span>Phone</span>
          <strong>
            {patient.phone_number ?? '—'}
          </strong>
        </div>

        <div>
          <span>Email</span>
          <strong>
            {patient.email ?? '—'}
          </strong>
        </div>

        <div>
          <span>Blood group</span>
          <strong>
            {patient.blood_group ?? '—'}
          </strong>
        </div>

        <div>
          <span>Genotype</span>
          <strong>
            {patient.genotype ?? '—'}
          </strong>
        </div>

      </div>


      <div className="patient-episodes">

        <div className="detail-header">

          <div>
            <p className="eyebrow">
              VISITS
            </p>

            <h3>
              Patient visits
            </h3>
          </div>

          {!episodeLoading &&
            !hasActiveEpisode() && (
            <button
              type="button"
              className="primary-button"
              onClick={onStartVisit}
              disabled={episodeActionLoading}
            >
              {episodeActionLoading
                ? 'Starting...'
                : 'Start visit'}
            </button>
          )}

        </div>


        {episodeLoading && (
          <p>
            Loading visits...
          </p>
        )}


        {episodeError && (
          <div className="login-error">
            {episodeError}
          </div>
        )}


        {!episodeLoading &&
          !episodeError &&
          episodes.length === 0 && (
          <p>
            No visits yet.
          </p>
        )}


        {!episodeLoading &&
          episodes.length > 0 && (
          <div>

            {episodes.map(episode => (
              <div
                className="permission-item"
                key={episode.id}
              >

                <div>
                  <strong>
                    {episode.episode_number}
                  </strong>

                  <span>
                    {episode.title}
                  </span>
                </div>

                <div>
                  <span>
                    {episode.flow_status}
                  </span>

                  {episode.flow_status ===
                    'AWAITING_CHECK_IN' && (
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() =>
                        onCheckIn(episode)
                      }
                      disabled={
                        episodeActionLoading
                      }
                    >
                      {episodeActionLoading
                        ? 'Checking in...'
                        : 'Check in'}
                    </button>
                  )}

                </div>

              </div>
            ))}

          </div>
        )}

      </div>

    </div>
  )
}