import { useEffect, useState } from "react";
import { useAuthStore } from "../../state/authStore";
import { ContentContainer, ContentLayout } from "../../Widgets/ContentLayout";
import { DropdownMenuSeparator } from "../../components/ui/dropdown-menu";

interface Config {
  bot_config: {
    id: string;
    profile_name: string;
    message_interface: {
      [key: string]: string;
    };
    web_interface: {
      [key: string]: string;
    };
    bot: {
      [key: string]: string;
    };
  };
  bot_memory: {
    mind_map: string;
    // eslint-disable-next-line @typescript-eslint/ban-types
    periodic_summaries: {};
    messages: {
      [timestamp: string]: {
        content: string;
        role: "system" | "assistant" | "user";
      };
    };
  };
}
export default function ConfigPage(): JSX.Element {
  const { backendUrl } = useAuthStore();

  const [config, setConfig] = useState<Config>();

  async function getConfig(): Promise<void> {
    const response = await fetch(`${backendUrl}/config`, {
      credentials: "include",
    }); // Include cookies for authentication
    console.log("response:", response.status);
    const responseData: Config = (await response.json()) as Config;
    console.log("responseData:", responseData);
    setConfig(responseData);
  }
  useEffect(() => {
    void getConfig();
  }, []);

  async function updateConfig(
    e: React.FormEvent<HTMLFormElement>,
  ): Promise<void> {
    e.preventDefault();
    const response = await fetch(`${backendUrl}/config`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config),
      credentials: "include",
    });
    const updatedConfig: Config = (await response.json()) as Config;
    console.log("Updated config:", updatedConfig);
    setConfig(updatedConfig);
  }

  // const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
  //   setConfig({ ...config, [e.target.name]: e.target.value });
  // };

  return config ? (
    <form onSubmit={void updateConfig}>
      <div
        className='m-4'
        // style={{
        //   margin: "15px",
        // }}
      >
        <ContentLayout>
          <>
            <div className='grid auto-rows-min gap-4 grid-cols-2 pt-5 pb-5'>
              <h1> Config</h1>
              <button type='submit'>Update Config</button>
            </div>
            <div className='grid auto-rows-min gap-4 xl:grid-cols-4 lg:grid-cols-2 pt-5 pb-5'>
              <Section sectionTitle='General'>
                <UserInput
                  label='id'
                  name='id'
                  value={config.bot_config?.id || ""}
                />
                <UserInput
                  label='profile_name'
                  name='profile_name'
                  value={config.bot_config?.profile_name || ""}
                />
              </Section>
              <Section sectionTitle='message_interface'>
                {Object.entries(config.bot_config.message_interface).map(
                  ([key, value]) => {
                    return (
                      <UserInput
                        key={key}
                        label={key}
                        name={key}
                        value={value || ""}
                      />
                    );
                  },
                )}
              </Section>
              <Section sectionTitle='web_interface'>
                {Object.entries(config.bot_config.web_interface).map(
                  ([key, value]) => {
                    return (
                      <UserInput
                        key={key}
                        label={key}
                        name={key}
                        value={value || ""}
                      />
                    );
                  },
                )}
              </Section>
              <Section sectionTitle='bot'>
                {Object.entries(config.bot_config.bot).map(([key, value]) => {
                  return (
                    <UserInput
                      key={key}
                      label={key}
                      name={key}
                      value={value || ""}
                    />
                  );
                })}
              </Section>
            </div>
            <div className='grid auto-rows-min gap-4 grid-cols-2 pt-5 pb-5'>
              <h1>Bot Memory</h1>
            </div>
            <>
              <Section sectionTitle='mind map' level={3}>
                <UserInput
                  label='mind_map'
                  name='mind_map'
                  value={config.bot_memory?.mind_map || ""}
                />
              </Section>
              <Section sectionTitle='periodic_summaries' level={3}>
                <>{JSON.stringify(config.bot_memory.periodic_summaries)}</>
              </Section>
              <Section sectionTitle='messages' level={3}>
                <div className='grid auto-rows-min gap-4 grid-cols-1 pt-5 pb-5'>
                  {Object.entries(config.bot_memory.messages).map(
                    ([timestamp, message]) => {
                      return (
                        <Section
                          sectionTitle={`message ${timestamp} role: ${message.role}`}
                          level={4}
                        >
                          <>{message.content}</>
                        </Section>
                      );
                    },
                  )}
                </div>
              </Section>
            </>
          </>
        </ContentLayout>
      </div>
    </form>
  ) : (
    <div>Loading...</div>
  );
}

function Section({
  sectionTitle,
  children,
  level = 3,
}: {
  sectionTitle: string;
  children: JSX.Element | JSX.Element[];
  level?: 2 | 3 | 4;
}): JSX.Element {
  return (
    <ContentContainer>
      <>
        {level === 2 ? (
          <h2>{sectionTitle}</h2>
        ) : level === 3 ? (
          <h3>{sectionTitle}</h3>
        ) : (
          <h4>{sectionTitle}</h4>
        )}
        <DropdownMenuSeparator />
        {children}
      </>
    </ContentContainer>
  );
}

function UserInput({
  label,
  name,
  value,
}: {
  label: string;
  name: string;
  value: string;
}): JSX.Element {
  return (
    <div style={{ width: "100%" }}>
      <label style={{ width: "100%" }}>{label}</label>
      <input style={{ width: "100%" }} name={name} value={value} />
    </div>
  );
}
