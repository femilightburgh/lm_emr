import type { Encounter } from '../../api/encounters'
import type { Episode } from '../../api/episodes'


interface Props {
  episodes: Episode[]
  currentEpisodeId: string | null

  selectedEpisode: Episode | null
  encounters: Encounter[]
  selectedEncounter: Encounter | null

  loading: boolean
  loadingHistorical: boolean

  onSelectEpisode: (
    episode: Episode,
  ) => void

  onSelectEncounter: (
    encounter: Encounter,
  ) => void
}


function formatDate(
  value: string | null,
): string {
  if (!value) {
    return '—'
  }

  return new Date(value).toLocaleString()
}


export default function PreviousEncountersPanel({
  episodes,
  currentEpisodeId,
  selectedEpisode,
  encounters,
  selectedEncounter,
  loading,
  loadingHistorical,
  onSelectEpisode,
  onSelectEncounter,
}: Props) {
  const previousEpisodes =
    episodes.filter(
      episode =>
        episode.id !== currentEpisodeId,
    )

  return (
    <section className="workspace-panel">
      <div className="panel-header">
        <div>
          <h2>Previous Episodes</h2>
          <p>
            Previous episodes of care and their encounters.
          </p>
        </div>
      </div>

      {loading && (
        <p>Loading previous episodes...</p>
      )}

      {!loading &&
        previousEpisodes.length === 0 && (
          <p>
            No previous episodes are available.
          </p>
        )}

      {!loading &&
        previousEpisodes.length > 0 && (
          <div className="stack">
            {previousEpisodes.map(episode => {
              const selected =
                selectedEpisode?.id === episode.id

              return (
                <div key={episode.id}>
                  <button
                    type="button"
                    className={
                      selected
                        ? 'list-item active'
                        : 'list-item'
                    }
                    onClick={() =>
                      onSelectEpisode(
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

                      {episode.closed_at && (
                        <>
                          {' · closed '}
                          {formatDate(
                            episode.closed_at,
                          )}
                        </>
                      )}
                    </span>
                  </button>

                  {selected && (
                    <div className="stack">
                      {loadingHistorical && (
                        <p>
                          Loading encounters...
                        </p>
                      )}

                      {!loadingHistorical &&
                        encounters.length === 0 && (
                          <p>
                            No encounters were recorded for this episode.
                          </p>
                        )}

                      {!loadingHistorical &&
                        encounters.map(encounter => (
                          <button
                            key={encounter.id}
                            type="button"
                            className={
                              selectedEncounter?.id === encounter.id
                                ? 'list-item active'
                                : 'list-item'
                            }
                            onClick={() =>
                              onSelectEncounter(
                                encounter,
                              )
                            }
                          >
                            <strong>
                              {encounter.title}
                            </strong>

                            <span>
                              {encounter.status}
                              {' · '}
                              {formatDate(
                                encounter.started_at,
                              )}
                            </span>
                          </button>
                        ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
    </section>
  )
}
