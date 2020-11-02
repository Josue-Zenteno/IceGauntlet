module IceGauntlet {

    exception Unauthorized{};

    interface Authentication {
        string getNewToken(string user, string passwordHash) throws Unauthorized;
        void changePassword(string user, string currentPassHash, string newPassHash) throws Unauthorized;
        bool isValid(string token);
    }
}
