import type { Episode } from '../../api/episodes'
import type { Patient } from '../../api/patients'

interface DoctorPatientBannerProps {
  patient: Patient | null
  loadingPatientContext: boolean
  selectedEpisode: Episode | null
  isWardReview: boolean
}

export default function DoctorPatientBanner({
  patient,
  loadingPatientContext,
  selectedEpisode,
  isWardReview,
}: DoctorPatientBannerProps) {
  return (
    <section
      className={`doctor-patient-banner ${
        isWardReview
          ? 'doctor-patient-banner--ward'
          : 'doctor-patient-banner--clinic'
      }`}
    >
      {loadingPatientContext ? (
        <div className="doctor-patient-banner-loading">
          Loading patient information...
        </div>
      ) : patient ? (
        <>
          <div className="doctor-patient-identity">
            <div className="doctor-patient-avatar">
              {patient.first_name.charAt(0)}
              {patient.last_name.charAt(0)}
            </div>

            <div>
              <p className="eyebrow">PATIENT</p>

              <h2>
                {patient.first_name}{' '}
                {patient.middle_name
                  ? `${patient.middle_name} `
                  : ''}
                {patient.last_name}
              </h2>

              <p>{patient.hospital_number}</p>
            </div>
          </div>

          <div className="doctor-patient-details">
            <div>
              <span>Date of birth</span>
              <strong>{patient.date_of_birth}</strong>
            </div>

            <div>
              <span>Sex</span>
              <strong>{patient.sex}</strong>
            </div>

            {selectedEpisode && (
              <div>
                <span>Episode</span>
                <strong>{selectedEpisode.episode_number}</strong>
              </div>
            )}

            {selectedEpisode && (
              <div>
                <span>Status</span>
                <strong>{selectedEpisode.status}</strong>
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="doctor-patient-banner-loading">
          Patient information unavailable.
        </div>
      )}
    </section>
  )
}
