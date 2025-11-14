import React, { useState } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons, MaterialIcons, FontAwesome5 } from '@expo/vector-icons';
import LoginScreen from "./screens/LoginScreen";
import HomeScreen from "./screens/HomeScreen";
import AttendanceScreen from "./screens/AttendanceScreen";
import ProfileScreen from "./screens/ProfileScreen";

const Tab = createBottomTabNavigator();

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  return (
    <NavigationContainer>
      {isLoggedIn && user ? (
        <Tab.Navigator
          screenOptions={({ route }) => ({
            headerShown: false,
            tabBarIcon: ({ focused, color, size }) => {
              if (route.name === 'Home') {
                return <Ionicons name={focused ? 'home' : 'home-outline'} size={28} color={color} />;
              } else if (route.name === 'Attendance') {
                return <MaterialIcons name="event-note" size={28} color={color} />;
              } else if (route.name === 'Profile') {
                return <FontAwesome5 name="user-alt" size={24} color={color} />;
              }
            },
            tabBarActiveTintColor: '#667eea',
            tabBarInactiveTintColor: '#9CA3AF',
            tabBarStyle: {
              backgroundColor: '#FFFFFF',
              borderTopWidth: 0,
              elevation: 20,
              shadowColor: '#000',
              shadowOffset: { width: 0, height: -4 },
              shadowOpacity: 0.1,
              shadowRadius: 8,
              height: 65,
              paddingBottom: 8,
              paddingTop: 8,
            },
            tabBarLabelStyle: {
              fontSize: 12,
              fontWeight: '600',
              marginBottom: 4,
            },
          })}
        >
          <Tab.Screen name="Home" options={{ tabBarLabel: 'Trang chủ' }}>
            {({ navigation }) => <HomeScreen user={user} navigation={navigation} />}
          </Tab.Screen>
          <Tab.Screen name="Attendance" options={{ tabBarLabel: 'Điểm danh' }}>
            {({ navigation }) => <AttendanceScreen user={user} navigation={navigation} />}
          </Tab.Screen>
          <Tab.Screen name="Profile" options={{ tabBarLabel: 'Cá nhân' }}>
            {({ navigation }) => <ProfileScreen user={user} navigation={navigation} onLogout={() => { setIsLoggedIn(false); setUser(null); }} />}
          </Tab.Screen>
        </Tab.Navigator>
      ) : (
        <LoginScreen onLogin={(userData) => { setUser(userData); setIsLoggedIn(true); }} />
      )}
    </NavigationContainer>
  );
}
