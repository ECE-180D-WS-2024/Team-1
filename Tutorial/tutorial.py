import wire_example
import sequence_example

def main():
    wire_example.init()

    while True:
        print("Starting the bomb defusal tutorial!")
        print("Please enter 's' to start or 'q' to quit :(")
        start = input()
        if start == 's':
            break
        elif start == 'q':
            return
        else:
            print('Unrecognized, please try again.')
            print()
            print()
    
    
    wire_example.start_wires()
    sequence_example.start_sequence()

if __name__ == "__main__":
    main()