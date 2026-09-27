import type { NursingIntakeFormState } from './nursing/types'

interface Props {
  intake: NursingIntakeFormState
  signedAt?: string | null
}

function Value({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="nursing-clinical-summary-field">
      <span>{label}</span>
      <strong>
        {value.trim() || '—'}
      </strong>
    </div>
  )
}

export default function NursingClinicalSummary({
  intake,
  signedAt,
}: Props) {
  return (
    <section className="nursing-section nursing-clinical-summary">
      <div className="nursing-section-heading">
        <div>
          <p className="eyebrow">
            CLINICAL CONTINUITY
          </p>

          <h3>
            Nursing assessment summary
          </h3>

          <p>
            Key findings documented during the nursing assessment.
          </p>
        </div>

        <span className="nursing-signed-badge">
          SIGNED
        </span>
      </div>

      {signedAt && (
        <div className="nursing-clinical-summary-meta">
          Signed {new Date(signedAt).toLocaleString()}
        </div>
      )}

      <div className="nursing-clinical-summary-grid">
        <div className="nursing-clinical-summary-group">
          <p className="eyebrow">
            PRESENTING PROBLEM
          </p>

          <Value
            label="Presenting complaint"
            value={intake.presenting_complaint}
          />

          <Value
            label="History of presenting complaint"
            value={intake.history_of_presenting_complaint}
          />
        </div>

        <div className="nursing-clinical-summary-group">
          <p className="eyebrow">
            MEDICAL BACKGROUND
          </p>

          <Value
            label="Known allergies"
            value={intake.known_allergies}
          />

          <Value
            label="Allergy notes"
            value={intake.allergy_notes}
          />

          <Value
            label="Past medical history"
            value={intake.past_medical_history}
          />

          <Value
            label="Current medications"
            value={intake.current_medications}
          />

          <Value
            label="Surgical history"
            value={intake.surgical_history}
          />
        </div>

        <div className="nursing-clinical-summary-group">
          <p className="eyebrow">
            CLINICAL ASSESSMENT
          </p>

          <Value
            label="General appearance"
            value={intake.general_appearance}
          />

          <Value
            label="Level of consciousness"
            value={intake.level_of_consciousness}
          />

          <Value
            label="Mobility"
            value={intake.mobility_status}
          />

          <Value
            label="Pain"
            value={
              intake.pain_score.trim()
                ? `${intake.pain_score}${intake.pain_location.trim() ? ` · ${intake.pain_location}` : ''}`
                : intake.pain_location
            }
          />
        </div>

        <div className="nursing-clinical-summary-group">
          <p className="eyebrow">
            RISK &amp; SAFETY
          </p>

          <Value
            label="Fall risk"
            value={intake.fall_risk}
          />

          <Value
            label="Pressure injury risk"
            value={intake.pressure_injury_risk}
          />

          <Value
            label="Infection precautions"
            value={intake.infection_precautions}
          />
        </div>

        <div className="nursing-clinical-summary-group nursing-clinical-summary-wide">
          <p className="eyebrow">
            NURSING OBSERVATIONS
          </p>

          <Value
            label="Nursing observations"
            value={intake.nursing_observations}
          />

          <Value
            label="Immediate concerns"
            value={intake.immediate_concerns}
          />
        </div>

        <div className="nursing-clinical-summary-group nursing-clinical-summary-wide">
          <p className="eyebrow">
            HANDOVER
          </p>

          <Value
            label="Handover notes"
            value={intake.handover_notes}
          />
        </div>
      </div>
    </section>
  )
}
