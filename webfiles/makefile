CC = gcc
CFLAGS = -Wall -Wextra -pedantic -g
TARGET = scraper

all: $(TARGET)

$(TARGET): scraper.o
	$(CC) $(CFLAGS) -o $(TARGET) scraper.o

scraper.o: scraper.c
	$(CC) $(CFLAGS) -c scraper.c

run: $(TARGET)
	@if [ "$(word 2, $(MAKECMDGOALS))" = "" ]; then \
		echo "Usage: make run <host> <port> <username> <message>"; \
	else \
		./$(TARGET) $(word 2, $(MAKECMDGOALS)) $(word 3, $(MAKECMDGOALS)) $(word 4, $(MAKECMDGOALS)) "$(wordlist 5,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))"; \
	fi

clean:
	rm -f $(TARGET) *.o

%:
	@:
