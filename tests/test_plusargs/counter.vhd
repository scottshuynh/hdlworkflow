library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity counter is
  generic (
    ADJUST       : positive;
    IS_DECREMENT : boolean
  );
  port (
    clk_i       : in std_logic;
    rst_i       : in std_logic;
    ce_i        : in std_logic             := '1';
    count_o     : out unsigned(7 downto 0) := (others => '0');
    count_vld_o : out std_logic            := '0'
  );
end entity;

architecture rtl of counter is

begin

  process (clk_i)
  begin
    if rising_edge(clk_i) then
      count_vld_o <= ce_i;
      if ce_i = '1' then
        if not IS_DECREMENT then
          count_o <= count_o + ADJUST;
        else
          count_o <= count_o - ADJUST;
        end if;
        if rst_i = '1' then
          count_o     <= (others => '0');
          count_vld_o <= '0';
        end if;
      end if;
    end if;
  end process;

end architecture;