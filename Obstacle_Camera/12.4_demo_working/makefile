NAME=run_Arducam_Demo
CC=g++
OPENCV_CFLAGS := $(shell pkg-config --cflags opencv4)
OPENCV_LIBS := $(shell pkg-config --libs opencv4)
CFLAGS += -I/usr/include/opencv4 -fpermissive $(OPENCV_CFLAGS)
LDFLAGS += $(OPENCV_LIBS)
ODIR=obj
SDIR=src

_DEPS=ArduCAM.h bcm283x_board_driver.h sccb_bus.h ov2640_regs.h ov5640_regs.h ov5642_regs.h
DEPS=$(patsubst %,$(SDIR)/%,$(_DEPS))

_OBJ=ArducamDemo.o ArduCAM.o bcm283x_board_driver.o sccb_bus.o
OBJ=$(patsubst %,$(ODIR)/%,$(_OBJ))

$(ODIR)/%.o: src/%.cpp $(DEPS)
	@mkdir -p $(@D)
	$(CC) -c -o $@ $< $(CFLAGS)

$(ODIR)/%.o: src/%.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

$(NAME): $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LDFLAGS)

.PHONY: run

run: $(NAME)
	sudo ./$(NAME)

.PHONY: clean
clean:	
	rm -f $(NAME) $(ODIR)/*.o
