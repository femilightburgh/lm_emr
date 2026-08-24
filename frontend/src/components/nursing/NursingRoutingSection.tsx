import type { Department } from '../../api/departments'


interface Props {
  departments: Department[]
  selectedDepartmentId: string
  loadingDepartments: boolean
  disabled: boolean
  routing: boolean
  routed: boolean

  onDepartmentChange: (
    departmentId: string,
  ) => void

  onRoute: () => void
}


export default function NursingRoutingSection({
  departments,
  selectedDepartmentId,
  loadingDepartments,
  disabled,
  routing,
  routed,
  onDepartmentChange,
  onRoute,
}: Props) {
  const selectedDepartment =
    departments.find(
      department =>
        department.id ===
        selectedDepartmentId,
    )


  if (routed) {
    return (
      <section className="nursing-section nursing-disposition nursing-disposition-routed">

        <div className="nursing-section-heading">

          <div>
            <p className="eyebrow">
              PATIENT DISPOSITION
            </p>

            <h3>
              Routing complete
            </h3>

            <p>
              The nursing assessment has been
              completed and the patient has been
              sent to the receiving department.
            </p>
          </div>

        </div>


        <div className="nursing-disposition-success">

          <div className="nursing-disposition-check">
            ✓
          </div>


          <div>

            <strong>
              Patient successfully routed
            </strong>

            <p>
              Destination:{' '}
              <strong>
                {selectedDepartment
                  ? selectedDepartment.name
                  : 'Department'}
              </strong>
            </p>

          </div>

        </div>

      </section>
    )
  }


  return (
    <section className="nursing-section nursing-disposition">

      <div className="nursing-section-heading">

        <div>
          <p className="eyebrow">
            PATIENT DISPOSITION
          </p>

          <h3>
            Route patient
          </h3>

          <p>
            Select the active clinical department
            that should receive this patient.
          </p>
        </div>

        <span className="nursing-signed-badge">
          INTAKE SIGNED
        </span>

      </div>


      <div className="nursing-routing-form">

        <label>
          <span>
            Destination department
          </span>

          <select
            value={
              selectedDepartmentId
            }
            onChange={event =>
              onDepartmentChange(
                event.target.value,
              )
            }
            disabled={
              disabled ||
              routing ||
              loadingDepartments
            }
          >

            <option value="">
              {loadingDepartments
                ? 'Loading departments...'
                : 'Select department'}
            </option>


            {departments.map(
              department => (
                <option
                  key={
                    department.id
                  }
                  value={
                    department.id
                  }
                >
                  {department.name}
                  {' '}
                  ({department.code})
                </option>
              ),
            )}

          </select>

          <small>
            Only active clinical departments
            are available for nursing routing.
          </small>
        </label>


        <div className="nursing-routing-action">

          <button
            type="button"
            className="primary-button"
            onClick={onRoute}
            disabled={
              disabled ||
              routing ||
              loadingDepartments ||
              !selectedDepartmentId
            }
          >
            {routing
              ? 'Routing patient...'
              : 'Route patient'}
          </button>

        </div>

      </div>

    </section>
  )
}
