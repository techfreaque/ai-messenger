import { useAuthStore } from "../state/authStore";
import { ContentContainer, ContentLayout } from "../Widgets/ContentLayout";

export default function HomePage(): JSX.Element {
  const { isLoggedIn } = useAuthStore();
  return (
    <ContentLayout>
      <ContentContainer>
        {isLoggedIn ? (
          <div>
            <h1>Welcome to the homepage</h1>
            <p>You are logged in</p>
          </div>
        ) : (
          <div>
            <h1>Not logged in</h1>
            <button>Login Now</button>
          </div>
        )}
      </ContentContainer>
    </ContentLayout>
  );
}
