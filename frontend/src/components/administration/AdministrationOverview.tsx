interface AdministrationOverviewProps {
  userCount: number
  roleCount: number
  onUsers: () => void
  onRoles: () => void
}


export default function AdministrationOverview({
  userCount,
  roleCount,
  onUsers,
  onRoles,
}: AdministrationOverviewProps) {
  return (
    <div className="admin-grid">

      <article className="admin-card">

        <span>
          Hospital users
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


      <article className="admin-card">

        <span>
          Hospital roles
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


      <article className="admin-card">

        <span>
          Authorization
        </span>

        <strong>
          RBAC
        </strong>

        <p>
          Hospital roles control access
          to platform capabilities.
        </p>

      </article>

    </div>
  )
}