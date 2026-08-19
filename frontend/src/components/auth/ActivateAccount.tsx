import {
  useState,
  type FormEvent,
} from 'react'

import {
  activateUser,
} from '../../api'


interface ActivateAccountProps {
  onActivated: () => void
}


export default function ActivateAccount({
  onActivated,
}: ActivateAccountProps) {

  const [token, setToken] =
    useState(
      new URLSearchParams(
        window.location.search,
      ).get('token') ?? '',
    )

  const [password, setPassword] =
    useState('')

  const [confirmPassword, setConfirmPassword] =
    useState('')

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  const [success, setSuccess] =
    useState(false)


  async function handleSubmit(
    event: FormEvent,
  ) {
    event.preventDefault()

    setError(null)

    if (!token.trim()) {
      setError(
        'Invitation code is required.',
      )
      return
    }

    if (password.length < 8) {
      setError(
        'Password must be at least 8 characters.',
      )
      return
    }

    if (password !== confirmPassword) {
      setError(
        'Passwords do not match.',
      )
      return
    }

    setLoading(true)

    try {
      await activateUser({
        token: token.trim(),
        password,
      })

      setSuccess(true)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to activate your account.',
      )
    } finally {
      setLoading(false)
    }
  }


  if (success) {
    return (
      <main className="login-shell">

        <section className="login-card">

          <div className="brand">
            LIGHTBURGH
          </div>

          <div className="workspace-name">
            Hospital Information System
          </div>

          <div className="login-heading">

            <p className="eyebrow">
              ACCOUNT ACTIVATION
            </p>

            <h1>
              Account activated
            </h1>

            <p className="login-subtitle">
              Your staff account is ready.
              You can now sign in using
              your hospital credentials.
            </p>

          </div>

          <button
            type="button"
            className="primary-button"
            style={{
              width: '100%',
              marginTop: '28px',
            }}
            onClick={onActivated}
          >
            Go to sign in
          </button>

        </section>

      </main>
    )
  }


  return (
    <main className="login-shell">

      <section className="login-card">

        <div className="brand">
          LIGHTBURGH
        </div>

        <div className="workspace-name">
          Hospital Information System
        </div>


        <div className="login-heading">

          <p className="eyebrow">
            STAFF ACCESS
          </p>

          <h1>
            Activate your account
          </h1>

          <p className="login-subtitle">
            Enter the invitation code provided
            by your hospital administrator and
            create your password.
          </p>

        </div>


        {error && (
          <div className="login-error">
            {error}
          </div>
        )}


        <form
          className="login-form"
          onSubmit={handleSubmit}
        >

          <label>

            Invitation code

            <input
              type="text"
              value={token}
              onChange={event =>
                setToken(
                  event.target.value,
                )
              }
              placeholder="Paste your invitation code"
              autoComplete="off"
              required
            />

          </label>


          <label>

            New password

            <input
              type="password"
              value={password}
              onChange={event =>
                setPassword(
                  event.target.value,
                )
              }
              placeholder="Create a password"
              autoComplete="new-password"
              minLength={8}
              required
            />

          </label>


          <label>

            Confirm password

            <input
              type="password"
              value={confirmPassword}
              onChange={event =>
                setConfirmPassword(
                  event.target.value,
                )
              }
              placeholder="Confirm your password"
              autoComplete="new-password"
              minLength={8}
              required
            />

          </label>


          <button
            type="submit"
            className="primary-button"
            disabled={loading}
          >
            {loading
              ? 'Activating...'
              : 'Activate account'}
          </button>

        </form>


        <button
          type="button"
          className="secondary-button"
          style={{
            width: '100%',
            marginTop: '10px',
          }}
          onClick={onActivated}
        >
          Back to sign in
        </button>

      </section>

    </main>
  )
}
