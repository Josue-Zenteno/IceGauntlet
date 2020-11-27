module IceGauntlet {

    exception Unauthorized{};
    exception RoomAlreadyExists{};
    exception RoomNotExists{}

    interface Authentication {
        string getNewToken(string user, string passwordHash) throws Unauthorized;
        void changePassword(string user, string currentPassHash, string newPassHash) throws Unauthorized;
        bool isValid(string token);
    }

    interface Game {
        string getRoom() throws RoomNotExists;
    }

    interface MapManagement {
        void publish(string token, string roomData) throws RoomAlreadyExists;
        void remove(string token, string roomName) throws RoomNotExists;
    }
}
