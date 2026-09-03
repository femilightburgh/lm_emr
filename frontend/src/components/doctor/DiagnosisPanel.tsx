import type {
  ClinicalDiagnosis,
  DiagnosisCertainty,
  DiagnosisType,
} from '../../api/diagnoses'

import type {
  TerminologyConcept,
} from '../../api/terminology'


interface Props {
  diagnoses: ClinicalDiagnosis[]
  loading: boolean
  saving: boolean
  encounterClosed: boolean

  eyebrow: string
  title: string
  description: string

  query: string
  results: TerminologyConcept[]
  selected: TerminologyConcept | null

  diagnosisType: DiagnosisType
  certainty: DiagnosisCertainty

  onQueryChange: (value: string) => void
  onSelect: (
    concept: TerminologyConcept,
  ) => void

  onDiagnosisTypeChange: (
    value: DiagnosisType,
  ) => void

  onCertaintyChange: (
    value: DiagnosisCertainty,
  ) => void

  onSave: () => void
}


export default function DiagnosisPanel({
  diagnoses,
  loading,
  saving,
  encounterClosed,

  eyebrow,
  title,
  description,

  query,
  results,
  selected,

  diagnosisType,
  certainty,

  onQueryChange,
  onSelect,

  onDiagnosisTypeChange,
  onCertaintyChange,

  onSave,
}: Props) {
  return (
    <section className="workspace-panel doctor-assessment-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">
            {eyebrow}
          </p>

          <h2>
            {title}
          </h2>

          <p>
            {description}
          </p>
        </div>

        <span>
          {diagnoses.length}
          {' '}
          {diagnoses.length === 1
            ? 'diagnosis'
            : 'diagnoses'}
        </span>
      </div>

      <div className="doctor-assessment-entry">
        <div className="doctor-diagnosis-search">
          <label>
            <span>
              Clinical diagnosis
            </span>

            <input
              disabled={encounterClosed}
              value={query}
              onChange={event =>
                onQueryChange(
                  event.target.value,
                )
              }
              placeholder="Search diagnosis or ICD-10-CM code"
            />
          </label>

          {results.length > 0 && (
            <div className="doctor-diagnosis-results">
              {results.map(concept => (
                <button
                  key={concept.id}
                  type="button"
                  className={
                    selected?.id === concept.id
                      ? 'doctor-diagnosis-result selected'
                      : 'doctor-diagnosis-result'
                  }
                  disabled={encounterClosed}
                  onClick={() =>
                    onSelect(concept)
                  }
                >
                  <span>
                    <strong>
                      {concept.display_name}
                    </strong>

                    <small>
                      {concept.system}
                      {' · '}
                      {concept.code}
                    </small>
                  </span>

                  {selected?.id === concept.id && (
                    <span className="doctor-diagnosis-check">
                      Selected
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {selected && (
          <div className="doctor-selected-diagnosis">
            <div>
              <p className="eyebrow">
                SELECTED
              </p>

              <strong>
                {selected.display_name}
              </strong>

              <span>
                {selected.system}
                {' · '}
                {selected.code}
              </span>
            </div>
          </div>
        )}

        <div className="doctor-diagnosis-options">
          <label>
            <span>
              Diagnosis type
            </span>

            <select
              disabled={encounterClosed}
              value={diagnosisType}
              onChange={event =>
                onDiagnosisTypeChange(
                  event.target.value as DiagnosisType,
                )
              }
            >
              <option value="DIFFERENTIAL">
                Differential
              </option>

              <option value="PROVISIONAL">
                Provisional
              </option>

              <option value="FINAL">
                Final
              </option>
            </select>
          </label>

          <label>
            <span>
              Certainty
            </span>

            <select
              disabled={encounterClosed}
              value={certainty}
              onChange={event =>
                onCertaintyChange(
                  event.target.value as DiagnosisCertainty,
                )
              }
            >
              <option value="SUSPECTED">
                Suspected
              </option>

              <option value="POSSIBLE">
                Possible
              </option>

              <option value="CONFIRMED">
                Confirmed
              </option>

              <option value="RULED_OUT">
                Ruled out
              </option>
            </select>
          </label>
        </div>

        <div className="doctor-assessment-action">
          <button
            type="button"
            className="primary-button"
            disabled={
              encounterClosed ||
              !selected ||
              saving
            }
            onClick={onSave}
          >
            {encounterClosed
              ? 'Encounter Closed'
              : saving
                ? 'Recording...'
                : 'Record Diagnosis'}
          </button>
        </div>
      </div>

      <div className="doctor-recorded-diagnoses">
        <div className="doctor-recorded-diagnoses-header">
          <div>
            <p className="eyebrow">
              RECORDED
            </p>

            <h3>
              Assessment History
            </h3>
          </div>
        </div>

        {loading && (
          <p className="doctor-assessment-empty">
            Loading diagnoses...
          </p>
        )}

        {!loading &&
          diagnoses.length === 0 && (
            <p className="doctor-assessment-empty">
              No clinical diagnoses recorded for this episode.
            </p>
          )}

        {!loading &&
          diagnoses.length > 0 && (
            <>
              {(
                [
                  {
                    type: 'PROVISIONAL' as DiagnosisType,
                    title: 'Working / Provisional',
                  },
                  {
                    type: 'DIFFERENTIAL' as DiagnosisType,
                    title: 'Differential Diagnoses',
                  },
                  {
                    type: 'FINAL' as DiagnosisType,
                    title: 'Final Diagnoses',
                  },
                ]
              ).map(group => {
                const groupDiagnoses =
                  diagnoses.filter(
                    diagnosis =>
                      diagnosis.diagnosis_type ===
                      group.type,
                  )

                if (groupDiagnoses.length === 0) {
                  return null
                }

                return (
                  <div
                    key={group.type}
                    className="doctor-assessment-group"
                  >
                    <div className="doctor-assessment-group-header">
                      <h4>
                        {group.title}
                      </h4>
                    </div>

                    {groupDiagnoses.map(
                      diagnosis => (
                        <div
                          key={diagnosis.id}
                          className="doctor-recorded-diagnosis"
                        >
                          <div>
                            <strong>
                              {diagnosis.diagnosis_name}
                            </strong>

                            <span>
                              {diagnosis.code_system &&
                                `${diagnosis.code_system} · `}
                              {diagnosis.code}
                            </span>

                            <small>
                              Recorded{' '}
                              {new Date(
                                diagnosis.diagnosed_at,
                              ).toLocaleString()}
                            </small>
                          </div>

                          <div className="doctor-diagnosis-badges">
                            <span>
                              {diagnosis.diagnosis_type}
                            </span>

                            <span>
                              {diagnosis.certainty}
                            </span>
                          </div>
                        </div>
                      ),
                    )}
                  </div>
                )
              })}
            </>
          )}
      </div>
    </section>
  )
}
