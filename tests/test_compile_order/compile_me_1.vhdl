library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity compile_me_1 is
  port (
    clk_i : in std_logic;
    rst_i : in std_logic;
    ce_i  : in std_logic := '1'
  );
end entity;

architecture rtl of compile_me_1 is
  signal count : unsigned(7 downto 0) := (others => '0');
begin

  process (clk_i)
  begin
    if rising_edge(clk_i) then
      if ce_i = '1' then
        count <= count + 2;
        if rst_i = '1' then
          count <= (others => '0');
        end if;
      end if;
    end if;
  end process;

end architecture;