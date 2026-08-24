interface VitalsForm {
  temperature: string
  heart_rate: string
  respiratory_rate: string
  systolic_bp: string
  diastolic_bp: string
  spo2: string
  weight: string
}


interface Props {
  vitals: VitalsForm
  disabled: boolean
  saving: boolean
  onChange: (
    field: keyof VitalsForm,
    value: string,
  ) => void
  onSave: () => void
}


interface VitalFieldProps {
  label: string
  unit?: string
  value: string
  type?: 'number'
  step?: string
  placeholder?: string
  disabled: boolean
  onChange: (
    value: string,
  ) => void
}


function VitalField({
  label,
  unit,
  value,
  type = 'number',
  step,
  placeholder,
  disabled,
  onChange,
}: VitalFieldProps) {
  return (
    <label className="nursing-vital-input">

      <span className="nursing-vital-input-label">
        {label}

        {unit && (
          <small>
            {unit}
          </small>
        )}
      </span>

      <input
        type={type}
        step={step}
        value={value}
        placeholder={placeholder}
        onChange={event =>
          onChange(
            event.target.value,
          )
        }
        disabled={disabled}
      />

    </label>
  )
}


export default function NursingVitalsForm({
  vitals,
  disabled,
  saving,
  onChange,
  onSave,
}: Props) {
  return (
    <section className="nursing-section nursing-vitals-entry">

      <div className="nursing-section-heading">

        <div>
          <p className="eyebrow">
            CLINICAL OBSERVATIONS
          </p>

          <h3>
            Record new vital signs
          </h3>

          <p>
            Enter the patient's current
            measurements. Fields may be
            completed independently.
          </p>
        </div>

      </div>


      <div className="nursing-vitals-entry-grid">

        <VitalField
          label="Temperature"
          unit="°C"
          value={
            vitals.temperature
          }
          step="0.1"
          placeholder="e.g. 36.8"
          disabled={disabled}
          onChange={value =>
            onChange(
              'temperature',
              value,
            )
          }
        />


        <VitalField
          label="Heart rate"
          unit="bpm"
          value={
            vitals.heart_rate
          }
          placeholder="e.g. 78"
          disabled={disabled}
          onChange={value =>
            onChange(
              'heart_rate',
              value,
            )
          }
        />


        <VitalField
          label="Respiratory rate"
          unit="/min"
          value={
            vitals.respiratory_rate
          }
          placeholder="e.g. 18"
          disabled={disabled}
          onChange={value =>
            onChange(
              'respiratory_rate',
              value,
            )
          }
        />


        <div className="nursing-bp-field">

          <div className="nursing-vital-input-label">
            <span>
              Blood pressure
            </span>

            <small>
              mmHg
            </small>
          </div>


          <div className="nursing-bp-inputs">

            <label>
              <span>
                Systolic
              </span>

              <input
                type="number"
                value={
                  vitals.systolic_bp
                }
                placeholder="120"
                onChange={event =>
                  onChange(
                    'systolic_bp',
                    event.target.value,
                  )
                }
                disabled={disabled}
              />
            </label>


            <span className="nursing-bp-separator">
              /
            </span>


            <label>
              <span>
                Diastolic
              </span>

              <input
                type="number"
                value={
                  vitals.diastolic_bp
                }
                placeholder="80"
                onChange={event =>
                  onChange(
                    'diastolic_bp',
                    event.target.value,
                  )
                }
                disabled={disabled}
              />
            </label>

          </div>

        </div>


        <VitalField
          label="SpO₂"
          unit="%"
          value={
            vitals.spo2
          }
          placeholder="e.g. 98"
          disabled={disabled}
          onChange={value =>
            onChange(
              'spo2',
              value,
            )
          }
        />


        <VitalField
          label="Weight"
          unit="kg"
          value={
            vitals.weight
          }
          step="0.1"
          placeholder="e.g. 72.5"
          disabled={disabled}
          onChange={value =>
            onChange(
              'weight',
              value,
            )
          }
        />

      </div>


      <div className="nursing-vitals-entry-actions">

        <button
          type="button"
          className="primary-button"
          onClick={onSave}
          disabled={
            disabled ||
            saving
          }
        >
          {saving
            ? 'Recording...'
            : 'Record vitals'}
        </button>

      </div>

    </section>
  )
}
