import { Component, type ErrorInfo, type ReactNode } from "react";

export type ErrorBoundaryProps = {
  children: ReactNode;
};

type ErrorBoundaryState = {
  hasError: boolean;
};

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(_error: Error, _info: ErrorInfo) {
    // The fallback intentionally avoids exposing technical error details.
  }

  render() {
    if (this.state.hasError) {
      return (
        <main className="error-boundary" role="alert">
          <div className="card error-boundary__card">
            <h1>Đã xảy ra lỗi giao diện</h1>
            <p>Trang gặp sự cố bất ngờ. Hãy tải lại hoặc quay về trang chủ.</p>
            <div className="action-bar action-bar--start">
              <button type="button" onClick={() => window.location.reload()}>
                Tải lại
              </button>
              <button type="button" className="secondary" onClick={() => window.location.assign("/")}>
                Về trang chủ
              </button>
            </div>
          </div>
        </main>
      );
    }

    return this.props.children;
  }
}
