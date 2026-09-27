import type { Encounter } from '../../api/encounters'
import type { Episode } from '../../api/episodes'

interface Props {
  selectedEncounter: Encounter | null
  selectedEpisode: Episode | null
}

export default function DoctorCurrentEncounterCard({
  selectedEncounter,
  selectedEpisode,
}: Props) {
  return (
    <section className="workspace-panel doctor-current-encounter">
      <div className="panel-header">
        <div>
          <p className="eyebrow">
            CURRENT ENCOUNTER
          </p>

          <h2>
            {selectedEncounter
              ? selectedEncounter.title
              : 'No encounter selected'}
          </h2>

          <p>
            {selectedEncounter
              ? 'Active clinical encounter.'
              : 'Select a patient from your queue to begin.'}
          </p>
        </div>

        {selectedEncounter && (
          <span>
            {selectedEncounter.status}
          </span>
        )}
      </div>

      {selectedEncounter ? (
        <div className="doctor-encounter-context">
          <div>
            <span>
              Episode
            </span>

            <strong>
              {selectedEpisode?.episode_number ?? '—'}
            </strong>
          </div>

          <div>
            <span>
              Episode status
            </span>

            <strong>
              {selectedEpisode?.status ?? '—'}
            </strong>
          </div>
        </div>
      ) : (
        <div className="doctor-encounter-empty">
          <p>
            No encounter selected.
          </p>
        </div>
      )}
    </section>
  )
}
