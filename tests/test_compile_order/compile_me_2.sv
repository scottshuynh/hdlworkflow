module compile_me_2 (
    input wire clk_i,
    input wire rst_i,
    input wire ce_i
);
    logic [7:0] count = 0;
    always @(posedge clk_i) begin
        if (ce_i) begin
            count <= count + 3;
            if (rst_i) begin
                count <= 0;
            end
        end
    end
endmodule