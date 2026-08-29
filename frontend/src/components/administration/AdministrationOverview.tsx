interface AdministrationOverviewProps {
  staffTotal: number
  userCount: number
  departmentCount: number
  roleCount: number
  staffWithoutAccountCount: number

  onUsers: () => void
  onStaff: () => void
  onDepartments: () => void
  onRoles: () => void
  onLaboratory: () => void
}


export default function AdministrationOverview({
  staffTotal,
  userCount,
  departmentCount,
  roleCount,
  staffWithoutAccountCount,
  onUsers,
  onStaff,
  onDepartments,
  onRoles,
  onLaboratory,
}: AdministrationOverviewProps) {
  return (
    <div className="admin-overview">

      <div className="admin-overview-metrics">

        <article className="admin-metric-card">
          <span>
            Active staff
          </span>

          <strong>
            {staffTotal}
          </strong>

          <button
            type="button"
            onClick={onStaff}
          >
            View staff
          </button>
        </article>


        <article className="admin-metric-card">
          <span>
            User accounts
          </span>

          <strong>
            {userCount}
          </strong>

          <button
            type="button"
            onClick={onUsers}
          >
            Manage users
          </button>
        </article>


        <article className="admin-metric-card">
          <span>
            Departments
          </span>

          <strong>
            {departmentCount}
          </strong>

          <button
            type="button"
            onClick={onDepartments}
          >
            Manage departments
          </button>
        </article>


        <article className="admin-metric-card">
          <span>
            Roles
          </span>

          <strong>
            {roleCount}
          </strong>

          <button
            type="button"
            onClick={onRoles}
          >
            Manage roles
          </button>
        </article>

      </div>


      <div className="admin-overview-grid">

        <section className="admin-overview-panel">
          <div className="admin-panel-header">
            <div>
              <h3>
                Administrative attention
              </h3>

              <p>
                Items that may need administrator action.
              </p>
            </div>
          </div>

          <button
            type="button"
            className="admin-overview-action"
            onClick={onStaff}
          >
            <span>
              Staff without LIGHTBURGH account
            </span>

            <strong>
              {staffWithoutAccountCount}
            </strong>
          </button>
        </section>


        <section className="admin-overview-panel">
          <div className="admin-panel-header">
            <div>
              <h3>
                Clinical configuration
              </h3>

              <p>
                Manage the hospital's clinical catalogues.
              </p>
            </div>
          </div>

          <button
            type="button"
            className="admin-overview-action"
            onClick={onLaboratory}
          >
            <span>
              Laboratory catalogue
            </span>

            <strong>
              Open
            </strong>
          </button>

          <div className="admin-overview-coming-soon">
            Medications · Procedures · Templates
          </div>
        </section>

      </div>


      <section className="admin-overview-panel">
        <div className="admin-panel-header">
          <div>
            <h3>
              Quick actions
            </h3>

            <p>
              Common administration tasks.
            </p>
          </div>
        </div>

        <div className="admin-overview-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={onStaff}
          >
            Staff directory
          </button>

          <button
            type="button"
            className="secondary-button"
            onClick={onUsers}
          >
            User accounts
          </button>

          <button
            type="button"
            className="secondary-button"
            onClick={onDepartments}
          >
            Departments
          </button>

          <button
            type="button"
            className="secondary-button"
            onClick={onRoles}
          >
            Roles
          </button>
        </div>
      </section>

    </div>
  )
}
