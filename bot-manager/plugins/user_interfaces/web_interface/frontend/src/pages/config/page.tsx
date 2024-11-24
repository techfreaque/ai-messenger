import { useBotStore } from "../../state/botStore";
import { ContentContainer, ContentLayout } from "../../Widgets/ContentLayout";
import { DropdownMenuSeparator } from "../../components/ui/dropdown-menu";

export default function ConfigPage(): JSX.Element {
  const { config, updateConfig } = useBotStore();
  return config ? (
    <form onSubmit={void updateConfig}>
      <div className='m-4'>
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
