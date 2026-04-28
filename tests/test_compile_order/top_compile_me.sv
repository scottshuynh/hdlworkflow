module top_compile_me (
  );

  reg clk_i = 1;
  reg rst_i = 1;
  reg ce_i = 1;

  always #1 clk_i = ! clk_i;

  initial begin
    #10;
    rst_i = 0;
    #128;
    $finish;
  end

  compile_me_2
    i_compile_me_2 (
      .clk_i(clk_i),
      .rst_i(rst_i),
      .ce_i(ce_i)
    );

  compile_me_3
    i_compile_me_3 (
      .clk_i(clk_i),
      .rst_i(rst_i),
      .ce_i(ce_i)
    );

endmodule
