import { SectionList, StatusBar, StyleSheet, Text, View } from "react-native";

import { matrixClient } from "@/context/MatrixClient";

export default function RoomList(): JSX.Element {
  const sections: { title: string; data: string[] }[] = [];
  const { rooms } = matrixClient();
  Object.values(rooms).forEach((room) => {
    sections.push({
      title: room.roomState.roomId,
      data: [],
    });
  });

  return (
    <SectionList
      sections={sections}
      keyExtractor={(item, index) => item}
      renderItem={({ item }) => (
        <View style={styles.item}>
          <Text style={styles.title}>{item}</Text>
        </View>
      )}
      renderSectionHeader={({ section: { title } }) => (
        <Text style={styles.header}>{title}</Text>
      )}
    />
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: StatusBar.currentHeight,
    marginHorizontal: 16,
  },
  item: {
    backgroundColor: "#f9c2ff",
    padding: 20,
    marginVertical: 8,
  },
  header: {
    fontSize: 32,
    backgroundColor: "#fff",
  },
  title: {
    fontSize: 24,
  },
});

//  <div>
//    <h2>Your Rooms</h2>
//    <ul>
//      {Object.entries(rooms)?.map(([roomId, room]) => (
//        <li key={roomId}>{room.info?.name || roomId}</li>
//      ))}
//    </ul>
//  </div>
