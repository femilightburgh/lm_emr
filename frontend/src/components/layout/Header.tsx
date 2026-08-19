import type { AuthenticatedUser } from '../../types'


type WorkspaceView =
  | 'dashboard'
  | 'patients'
  | 'register'
  | 'administrator'


interface HeaderProps {
  user: AuthenticatedUser
  view: WorkspaceView
  isReceptionist: boolean
}


function getWorkspaceTitle(
  view: WorkspaceView,
): string {
  switch (view) {
    case 'dashboard':
      return 'Good day'

    case 'patients':
      return 'Patients'

    case 'register':
      return 'Register patient'

    case 'administrator':
      return 'Administration'

    default:
      return 'LIGHTBURGH'
  }
}


export default function Header({
  user,
  view,
  isReceptionist,
}: HeaderProps) {
  return (
    <header className="workspace-header">

      <div>

        <p className="eyebrow">
          {isReceptionist
            ? 'RECEPTION'
            : 'STAFF WORKSPACE'}
        </p>

        <h1>
          {getWorkspaceTitle(view)}
        </h1>

      </div>


      <div className="header-user">
        <span>
          {user.email}
        </span>
      </div>

    </header>
  )
}