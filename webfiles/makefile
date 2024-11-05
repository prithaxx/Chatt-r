# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -pedantic -g
TARGET = scraper

# Build target
all: $(TARGET)

# Link and compile the target
$(TARGET): scraper.o
	$(CC) $(CFLAGS) -o $(TARGET) scraper.o

# Compile the object file
scraper.o: scraper.c
	$(CC) $(CFLAGS) -c scraper.c

# Run the program with positional arguments
run: $(TARGET)
	@if [ "$(word 2, $(MAKECMDGOALS))" = "" ]; then \
		echo "Usage: make run <host> <port> <username> <message>"; \
	else \
		./$(TARGET) $(word 2, $(MAKECMDGOALS)) $(word 3, $(MAKECMDGOALS)) $(word 4, $(MAKECMDGOALS)) "$(wordlist 5,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))"; \
	fi

# Clean up object files and binary
clean:
	rm -f $(TARGET) *.o

# Ignore the extra arguments after `make run`
%:
	@:
