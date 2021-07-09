#include <sqlite3.h>
#include <stdio.h>

int main() {
    sqlite3* db;
    char buffer[64], buffer2[64];
    int bpos = 0;
    char c;
    struct sqlite3_stmt* stmt;
    FILE* txtfile;

    sqlite3_open_v2("engldict_a.db", &db, SQLITE_OPEN_CREATE | SQLITE_OPEN_READWRITE, NULL);

    sqlite3_prepare_v3(db, "CREATE TABLE words (word TEXT);", 32, 0, &stmt, NULL);
    sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    txtfile = fopen("english_dict_a2.txt", "r");
    while (!feof(txtfile)) {
        c = fgetc(txtfile);
        if (c == '\n') {
            buffer[bpos] = 0;
            bpos = sprintf(buffer2, "INSERT INTO words (word) VALUES (\"%s\");", buffer);
            sqlite3_prepare_v3(db, buffer2, bpos + 1, 0, &stmt, NULL);
            sqlite3_step(stmt);
            sqlite3_finalize(stmt);

            bpos = 0;
        } else buffer[bpos++] = c;
    }
    fclose(txtfile);
    sqlite3_close_v2(db);
}
