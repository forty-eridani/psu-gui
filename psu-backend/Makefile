SRC := ./c/*.c
INCLUDE_DIR := ./include/
CC := gcc
EXE := build/out
FLAGS := -g

$(EXE): $(SRC) $(INCLUDE)
	$(CC) $(SRC) -I $(INCLUDE_DIR) $(FLAGS) -o $@
