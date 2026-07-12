module blinky 
#(
    parameter led_toggle_period_cycles = 100_000_000
)
( 
    input wire clk_i,
    output reg led_o
);

    reg [$clog2(led_toggle_period_cycles)-1:0] count = 0;
    reg [$clog2(led_toggle_period_cycles)-1:0] next_count;
    always_comb begin
        next_count <= count + 1;
    end
        
    always @(posedge clk_i) begin
        count <= count + 1;
        if (next_count == led_toggle_period_cycles) begin
            led_o <= !led_o;
            count <= 0;
        end
    end
    
endmodule