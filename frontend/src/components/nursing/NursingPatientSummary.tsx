import type { Episode } from '../../api/episodes'
import type { Encounter } from '../../api/encounters'
import type { Patient } from '../../types'

interface PreviousVisit {
  episode: Episode
  encounters: Encounter[]
  eventsByEncounter: Record<string, unknown[]>
}

interface Props {
  episode: Episode
  encounter: Encounter
  patient: Patient | null
  loadingPatient: boolean
  previousEpisodes: Episode[]
  loadingPreviousEpisodes: boolean
  previousVisits: PreviousVisit[]
  loadingPreviousVisits: boolean
}

function fullName(patient: Patient | null): string {
  if (!patient) return 'Patient'
  return [patient.first_name, patient.middle_name, patient.last_name].filter(Boolean).join(' ')
}

function ageFromDob(value: string | null | undefined): string {
  if (!value) return 'Age —'
  const dob = new Date(value)
  const today = new Date()
  let age = today.getFullYear() - dob.getFullYear()
  if (today.getMonth() < dob.getMonth() || (today.getMonth() === dob.getMonth() && today.getDate() < dob.getDate())) age--
  return `${age} years`
}

function date(value: string | null | undefined): string {
  if (!value) return '—'
  return new Date(value).toLocaleDateString([], { day: '2-digit', month: 'short', year: 'numeric' })
}

function dateTime(value: string): string {
  return new Date(value).toLocaleString([], { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

export default function NursingPatientSummary({
  episode, encounter, patient, loadingPatient, previousEpisodes, loadingPreviousEpisodes, previousVisits, loadingPreviousVisits,
}: Props) {
  const name = fullName(patient)
  return (
    <section className="nursing-patient-cockpit">
      <header className="nursing-cockpit-header">
        <div className="nursing-cockpit-identity">
          <span className="nursing-cockpit-avatar">
            {name.split(' ').map(part => part.charAt(0)).slice(0, 2).join('')}
          </span>
          <div>
            <p className="eyebrow">PATIENT SNAPSHOT</p>
            <h2>{loadingPatient ? 'Loading patient…' : name}</h2>
            <p>{patient?.hospital_number ?? 'Hospital number —'} · {patient?.sex ?? 'Sex —'} · {ageFromDob(patient?.date_of_birth)}</p>
          </div>
        </div>
        <div className="nursing-cockpit-status">
          <span className="nursing-status-pill">OPEN</span>
          <small>{episode.title}</small>
          <strong>{episode.episode_number}</strong>
        </div>
      </header>

      <div className="nursing-cockpit-alerts">
        <div>
          <span>Blood group</span>
          <strong>{patient?.blood_group ?? 'Not recorded'}</strong>
        </div>
        <div>
          <span>Genotype</span>
          <strong>{patient?.genotype ?? 'Not recorded'}</strong>
        </div>
        <div className="nursing-cockpit-alert">
          <span>Allergies</span>
          <strong>Review nursing intake</strong>
        </div>
        <div>
          <span>Encounter started</span>
          <strong>{dateTime(encounter.started_at)}</strong>
        </div>
      </div>

      <div className="nursing-context-grid">
        <details open className="nursing-context-card">
          <summary><span><small>CARE CONTEXT</small><strong>Current episode</strong></span><b>{episode.status}</b></summary>
          <div className="nursing-context-body">
            <div><span>Episode</span><strong>{episode.episode_number}</strong></div>
            <div><span>Visit</span><strong>{episode.title}</strong></div>
            <div><span>Encounter</span><strong>{encounter.title}</strong></div>
            <div><span>Started</span><strong>{dateTime(encounter.started_at)}</strong></div>
          </div>
        </details>

        <details className="nursing-context-card">
          <summary><span><small>BACKGROUND</small><strong>Patient information</strong></span><b>View</b></summary>
          <div className="nursing-context-body">
            <div><span>Phone</span><strong>{patient?.phone_number ?? '—'}</strong></div>
            <div><span>Next of kin</span><strong>{patient?.next_of_kin_name ?? '—'}</strong></div>
            <div><span>Relationship</span><strong>{patient?.next_of_kin_relationship ?? '—'}</strong></div>
            <div><span>Date of birth</span><strong>{date(patient?.date_of_birth)}</strong></div>
          </div>
        </details>

        <details className="nursing-context-card">
          <summary><span><small>CARE HISTORY</small><strong>Previous visits</strong></span><b>{loadingPreviousEpisodes ? '…' : previousEpisodes.length}</b></summary>
          <div className="nursing-history-body">
            {loadingPreviousVisits || loadingPreviousEpisodes ? 'Loading history…' : previousVisits.length === 0 ? 'No previous visits recorded.' : previousVisits.slice(0, 5).map(visit => (
              <div key={visit.episode.id} className="nursing-history-row">
                <div><strong>{visit.episode.title}</strong><span>{visit.episode.episode_number}</span></div>
                <small>{visit.encounters.length} encounter{visit.encounters.length === 1 ? '' : 's'}</small>
              </div>
            ))}
          </div>
        </details>
      </div>
    </section>
  )
}
