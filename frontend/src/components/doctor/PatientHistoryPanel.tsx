import type { Encounter } from '../../api/encounters'
import type { Episode } from '../../api/episodes'


interface Props {
  currentEpisode: Episode | null

  previousEpisodes: Episode[]
  selectedEpisode: Episode | null

  currentEpisodeEncounters: Encounter[]
  historicalEncounters: Encounter[]
  selectedHistoricalEncounter: Encounter | null

  loadingCurrentEncounters: boolean
  loadingPreviousEpisodes: boolean
  loadingHistorical: boolean

  onSelectCurrentEncounter: (
    encounter: Encounter,
  ) => void

  onSelectPreviousEpisode: (
    episode: Episode,
  ) => void

  onSelectHistoricalEncounter: (
    encounter: Encounter,
  ) => void
}


function formatDate(
  value: string | null | undefined,
): string {
  if (!value) {
    return '—'
  }

  return new Date(value).toLocaleString()
}


function encounterLabel(
  encounter: Encounter,
  encounters: Encounter[],
): string {
  const sameTitle =
    encounters.filter(
      item =>
        item.title === encounter.title,
    )

  if (sameTitle.length <= 1) {
    return encounter.title
  }

  const index =
    sameTitle.findIndex(
      item => item.id === encounter.id,
    )

  return `${encounter.title} #${index + 1}`
}


export default function PatientHistoryPanel({
  currentEpisode,
  previousEpisodes,
  selectedEpisode,
  currentEpisodeEncounters,
  historicalEncounters,
  selectedHistoricalEncounter,

  loadingCurrentEncounters,
  loadingPreviousEpisodes,
  loadingHistorical,

  onSelectCurrentEncounter,
  onSelectPreviousEpisode,
  onSelectHistoricalEncounter,
}: Props) {
  return (
    <section className="workspace-panel doctor-patient-history">
      <details>
        <summary className="doctor-context-summary">
          <div>
            <p className="eyebrow">
              CARE CONTEXT
            </p>

            <h2>
              Encounter History
            </h2>

            <p>
              Current episode activity and previous episodes of care.
            </p>
          </div>

          <div className="doctor-context-summary-meta">
            {currentEpisode && (
              <span>
                {currentEpisode.episode_number}
              </span>
            )}

            <span>
              {previousEpisodes.length}
              {' '}
              past
              {previousEpisodes.length === 1
                ? ' episode'
                : ' episodes'}
            </span>
          </div>
        </summary>

        <div className="doctor-context-body">
          {currentEpisode && (
            <div className="diagnosis-list">
              <h3>
                Current Episode
              </h3>

              <div className="selected-diagnosis">
                <strong>
                  {currentEpisode.episode_number}
                  {' · '}
                  {currentEpisode.title}
                </strong>

                <span>
                  {currentEpisode.status}
                  {' · opened '}
                  {formatDate(
                    currentEpisode.opened_at,
                  )}
                </span>
              </div>

              <div className="stack">
                {loadingCurrentEncounters && (
                  <p>
                    Loading current encounters...
                  </p>
                )}

                {!loadingCurrentEncounters &&
                  currentEpisodeEncounters.length === 0 && (
                    <p>
                      No encounters recorded for this episode.
                    </p>
                  )}

                {!loadingCurrentEncounters &&
                  currentEpisodeEncounters.map(
                    encounter => (
                      <button
                        key={encounter.id}
                        type="button"
                        className="list-item"
                        onClick={() =>
                          onSelectCurrentEncounter(
                            encounter,
                          )
                        }
                      >
                        <strong>
                          {encounterLabel(
                            encounter,
                            currentEpisodeEncounters,
                          )}
                        </strong>

                        <span>
                          {encounter.status}
                          {' · '}
                          {formatDate(
                            encounter.started_at,
                          )}
                        </span>
                      </button>
                    ),
                  )}
              </div>
            </div>
          )}

          <details className="doctor-past-episodes">
            <summary>
              Past Episodes
              {' '}
              ({previousEpisodes.length})
            </summary>

            <div className="doctor-past-episodes-body">
              {loadingPreviousEpisodes && (
                <p>
                  Loading past episodes...
                </p>
              )}

              {!loadingPreviousEpisodes &&
                previousEpisodes.length === 0 && (
                  <p>
                    No previous episodes are available.
                  </p>
                )}

              {!loadingPreviousEpisodes &&
                previousEpisodes.map(
                  episode => {
                    const selected =
                      selectedEpisode?.id === episode.id

                    return (
                      <div
                        key={episode.id}
                        className="doctor-history-episode"
                      >
                        <button
                          type="button"
                          className={
                            selected
                              ? 'list-item active'
                              : 'list-item'
                          }
                          onClick={() =>
                            onSelectPreviousEpisode(
                              episode,
                            )
                          }
                        >
                          <strong>
                            {episode.episode_number}
                            {' · '}
                            {episode.title}
                          </strong>

                          <span>
                            {episode.status}
                            {' · opened '}
                            {formatDate(
                              episode.opened_at,
                            )}
                          </span>
                        </button>

                        {selected && (
                          <div className="stack doctor-history-encounters">
                            {loadingHistorical && (
                              <p>
                                Loading historical encounters...
                              </p>
                            )}

                            {!loadingHistorical &&
                              historicalEncounters.length === 0 && (
                                <p>
                                  No encounters recorded for this episode.
                                </p>
                              )}

                            {!loadingHistorical &&
                              historicalEncounters.map(
                                encounter => (
                                  <button
                                    key={encounter.id}
                                    type="button"
                                    className={
                                      selectedHistoricalEncounter?.id ===
                                      encounter.id
                                        ? 'list-item active'
                                        : 'list-item'
                                    }
                                    onClick={() =>
                                      onSelectHistoricalEncounter(
                                        encounter,
                                      )
                                    }
                                  >
                                    <strong>
                                      {encounterLabel(
                                        encounter,
                                        historicalEncounters,
                                      )}
                                    </strong>

                                    <span>
                                      {encounter.status}
                                      {' · '}
                                      {formatDate(
                                        encounter.started_at,
                                      )}
                                    </span>
                                  </button>
                                ),
                              )}
                          </div>
                        )}
                      </div>
                    )
                  },
                )}
            </div>
          </details>
        </div>
      </details>
    </section>
  )
}
